#!/usr/bin/env python3

import os
import shutil
import logging
import argparse

from pprint import pprint
from colorlog import ColoredFormatter
import exiftool


formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s : %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)


log = logging.getLogger()
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

raw = ['CR2', 'ORF', 'TIFF']
no_naw = ['JPG', 'PNG', 'GIF', 'JPEG']


def listdir_fullpath(d):
    return sorted([os.path.join(d, f) for f in os.listdir(d)])


def outdir_name(file, outdir, sorttypes):
    if sorttypes:
        if file.split('.')[-1:][0] in raw:
            return os.path.join(outdir, 'RAW')
        elif file.split('.')[1] in no_naw:
            return os.path.join(outdir, 'NON_RAW')
        else:
            return os.path.join(outdir, 'NON_RAW')
    else:
        log.debug('sorttypes disabled')
        return outdir


def get_file_date(file):
    with exiftool.ExifTool() as et:
        d = et.get_metadata(file)
        try:
            log.debug('🜏 {}: {}'.format(
                file, d['EXIF:DateTimeOriginal'].split()[0]))
            return d['EXIF:DateTimeOriginal'].split()[0]
            try:
                log.debug('d {}: {}'.format(
                    file, d['Composite:DateTimeOriginal'].split()[0]))
                return d['Composite:DateTimeOriginal'].split()[0]
            except:
                log.debug(' {}: {}'.format(
                    file, d['File:FileModifyDate'].split()[0]))
                return d['File:FileModifyDate'].split()[0]
        except:
            log.debug('⛧ {}: {}'.format(
                file, d['File:FileModifyDate'].split()[0]))
            return d['File:FileModifyDate'].split()[0]


def copy_move(filedescr):
    if filedescr['move']:
        log.info('Moving {} to {}'.format(
            filedescr['oldpath'], filedescr['newpath']))
        if not filedescr['dryrun']:
            try:
                shutil.move(filedescr['oldpath'], filedescr['newpath'])
            except Exception as e:
                log.error(e)
    else:
        log.info('Copying {} to {}'.format(
            filedescr['oldpath'], filedescr['newpath']))
        if not filedescr['dryrun']:
            try:
                shutil.copy2(filedescr['oldpath'], filedescr['newpath'])
            except Exception as e:
                log.error(e)


def sort_img(dir, outdir, move=True, dryrun=False, sorttypes=False):
    log.info('Processing {}'.format(dir))

    files = sorted(listdir_fullpath(dir))
    log.debug(files)
    filelist = []
    # Python indexes start at zero
    for index, file in enumerate(files, start=0):

        filesdesc = {'oldpath': file, 'move': move, 'dryrun': dryrun}
        filesdesc['date'] = get_file_date(file)

        if file.split('.')[-1:][0].upper() == 'XMP':
            if file.split('.')[0] == files[index - 1].split('.')[0]:
                filesdesc['date'] = filelist[index - 1]['date']

        try:
            (year, month, day) = filesdesc['date'].split(':')
            filesdesc['newpath'] = '{}/{}/{}/{}'.format(
                outdir_name(file, outdir, sorttypes), year, month, day)
        except:
            log.error('Date format wrong')

        if file.split('.')[-1:][0].upper() == 'XMP':
            if file.split('.')[0] == files[index - 1].split('.')[0]:
                filesdesc['newpath'] = filelist[index - 1]['newpath']

        log.debug(filesdesc['newpath'])
        log.debug('Adding {}'.format(filesdesc['newpath']))
        if not dryrun:
            os.makedirs('{}'.format(filesdesc['newpath']), exist_ok=True)

        copy_move(filesdesc)
        filelist.append(filesdesc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="Input directory")
    parser.add_argument(
        "-o", "--outdir", help="Output directory", default=os.getcwd())
    parser.add_argument(
        "-c", "--copy", help="Copys the images instead of moving them", action="store_true")
    parser.add_argument(
        "-t", "--testrun", help="Doesn't copy or move any files, does not make any dirs", action="store_true")
    parser.add_argument("-v", "--verbosity",
                        help="Increase output verbosity", action="count",)
    parser.add_argument("-s", "--separate_dirs",
                        help="Make separate dirs for raw and non raw files", action="store_true")
    args = parser.parse_args()

    if args.verbosity == 2:
        log.setLevel(logging.DEBUG)
    elif args.verbosity == 1:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    indir = args.indir
    outdir = args.outdir
    move = not args.copy
    dryrun = args.testrun
    sorttypes = args.separate_dirs

    log.info('Settings:')
    log.info('Input directory:              {}'.format(indir))
    log.info('Output directory:             {}'.format(outdir))
    log.info('Move files:                   {}'.format(move))
    log.info('Testrun:                      {}'.format(dryrun))
    log.info('Sort files according to type: {}'.format(sorttypes))
    log.info('⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧⛧')

    sort_img(indir, outdir, move, dryrun, sorttypes)


if __name__ == '__main__':
    main()
