#!/usr/bin/env python
""" COCO validation script

Hacked together by Ross Wightman (https://github.com/rwightman)
"""
import argparse
import os
import json
import time
import logging
import torch
import torch.nn.parallel
try:
    from apex import amp
    has_amp = True
except ImportError:
    has_amp = False

from effdet import create_model
from data import create_loader, CocoDetection
from timm.utils import AverageMeter, setup_default_logging

from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


torch.backends.cudnn.benchmark = True


def add_bool_arg(parser, name, default=False, help=''):  # FIXME move to utils
    dest_name = name.replace('-', '_')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=dest_name, action='store_true', help=help)
    group.add_argument('--no-' + name, dest=dest_name, action='store_false', help=help)
    parser.set_defaults(**{dest_name: default})


parser = argparse.ArgumentParser(description='PyTorch ImageNet Validation')
parser.add_argument('data', metavar='DIR',
                    help='path to dataset')
parser.add_argument('--anno', default='val2017',
                    help='mscoco annotation set (one of val2017, train2017, test-dev2017)')
parser.add_argument('--model', '-m', metavar='MODEL', default='tf_efficientdet_d1',
                    help='model architecture (default: tf_efficientdet_d1)')
add_bool_arg(parser, 'redundant-bias', default=None,
                    help='override model config for redundant bias layers')
parser.add_argument('-j', '--workers', default=4, type=int, metavar='N',
                    help='number of data loading workers (default: 4)')
parser.add_argument('-b', '--batch-size', default=128, type=int,
                    metavar='N', help='mini-batch size (default: 128)')
parser.add_argument('--img-size', default=None, type=int,
                    metavar='N', help='Input image dimension, uses model default if empty')
parser.add_argument('--mean', type=float, nargs='+', default=None, metavar='MEAN',
                    help='Override mean pixel value of dataset')
parser.add_argument('--std', type=float,  nargs='+', default=None, metavar='STD',
                    help='Override std deviation of of dataset')
parser.add_argument('--interpolation', default='bilinear', type=str, metavar='NAME',
                    help='Image resize interpolation type (overrides model)')
parser.add_argument('--fill-color', default='mean', type=str, metavar='NAME',
                    help='Image augmentation fill (background) color ("mean" or int)')
parser.add_argument('--log-freq', default=10, type=int,
                    metavar='N', help='batch logging frequency (default: 10)')
parser.add_argument('--checkpoint', default='', type=str, metavar='PATH',
                    help='path to latest checkpoint (default: none)')
parser.add_argument('--pretrained', dest='pretrained', action='store_true',
                    help='use pre-trained model')
parser.add_argument('--num-gpu', type=int, default=1,
                    help='Number of GPUS to use')
parser.add_argument('--no-prefetcher', action='store_true', default=False,
                    help='disable fast prefetcher')
parser.add_argument('--pin-mem', action='store_true', default=False,
                    help='Pin CPU memory in DataLoader for more efficient (sometimes) transfer to GPU.')
parser.add_argument('--use-ema', dest='use_ema', action='store_true',
                    help='use ema version of weights if present')
parser.add_argument('--torchscript', dest='torchscript', action='store_true',
                    help='convert model torchscript for inference')
parser.add_argument('--results', default='./results.json', type=str, metavar='FILENAME',
                    help='JSON filename for evaluation results')


def validate(args):
    setup_default_logging()

    # might as well try to validate something
    args.pretrained = args.pretrained or not args.checkpoint
    args.prefetcher = not args.no_prefetcher

    # create model
    bench = create_model(
        args.model,
        bench_task='predict',
        pretrained=args.pretrained,
        redundant_bias=args.redundant_bias,
        checkpoint_path=args.checkpoint,
        checkpoint_ema=args.use_ema
    )
    input_size = bench.config.image_size

    param_count = sum([m.numel() for m in bench.parameters()])
    print('Model %s created, param count: %d' % (args.model, param_count))

    bench = bench.cuda()
    if has_amp:
        print('Using AMP mixed precision.')
        bench = amp.initialize(bench, opt_level='O1')
    else:
        print('AMP not installed, running network in FP32.')

    if args.num_gpu > 1:
        bench = torch.nn.DataParallel(bench, device_ids=list(range(args.num_gpu)))

    if 'test' in args.anno:
        annotation_path = os.path.join(args.data, 'annotations', f'image_info_{args.anno}.json')
        image_dir = args.anno
    else:
        annotation_path = os.path.join(args.data, 'annotations', f'instances_{args.anno}.json')
        image_dir = args.anno
    dataset = CocoDetection(os.path.join(args.data, image_dir), annotation_path)

    loader = create_loader(
        dataset,
        input_size=input_size,
        batch_size=args.batch_size,
        use_prefetcher=args.prefetcher,
        interpolation=args.interpolation,
        fill_color=args.fill_color,
        num_workers=args.workers,
        mean = args.mean,
        std=args.std,
        pin_mem=args.pin_mem)

    img_ids = []
    results = []
    bench.eval()



    for i, (input, target) in enumerate(loader,1):
        dumm_inp = input
        tisc = target['img_scale']
        tisz = target['img_size']
        break

    starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    # repetitions = 300
    # timings=np.zeros((repetitions,1))
    #GPU-WARM-UP
    # print(enumerate())
    for _ in range(10):
        _ = bench(dumm_inp, tisc, tisz)
    # MEASURE PERFORMANCE

    # dummy_input = torch.randn(1, 3,bench.config.image_size,bench.config.image_size,dtype=torch.float).to("cuda")
    print("starting")
    batch_time = AverageMeter()
    # end = time.time()
    with torch.no_grad():
        for _ in range(2000):
            starter.record()
            _ = bench(dumm_inp, tisc, tisz)
            ender.record()
            # measure elapsed time
            torch.cuda.synchronize()
            curr_time = starter.elapsed_time(ender)
            batch_time.update(curr_time)
            # print(curr_time)
            # end = time.time()

            # if i % args.log_freq == 0:
            print(
                'Test: [{0:>4d}/{1}]  '
                'Time: {batch_time.val:.3f}ms ({batch_time.avg:.3f}ms, {rate_avg:>7.2f}/s)  '
                .format(
                    i, len(loader), batch_time=batch_time,
                    rate_avg=dumm_inp.size(0) / batch_time.avg,
                    )
            )
    
    # json.dump(results, open(args.results, 'w'), indent=4)
    # if 'test' not in args.anno:
    #     coco_results = dataset.coco.loadRes(args.results)
    #     coco_eval = COCOeval(dataset.coco, coco_results, 'bbox')
    #     coco_eval.params.imgIds = img_ids  # score only ids we've used
    #     coco_eval.evaluate()
    #     coco_eval.accumulate()
    #     coco_eval.summarize()

    return results


def main():
    args = parser.parse_args()
    validate(args)


if __name__ == '__main__':
    main()

