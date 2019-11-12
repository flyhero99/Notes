# coding=utf-8
import argparse
import json

import os
import re
from collections import namedtuple
import sys

SummaryStructured = namedtuple('SummaryStructured', 'type key path depth')

ignored = set()
summary_structured = []


def error(msg, code=1):
    print >>sys.stderr, 'ERROR: '+msg
    print >>sys.stderr, 'Abort!'
    exit(code)


def gen_anchor(path):
    filtered = '`,.:_()'
    path = path.lower()
    for f in filtered:
        path = path.replace(f, '')
    path = path.replace(' ', '-')
    return path


def parse_md(key, path, depth):
    pattern = re.compile(r'(#+)(.*)')
    for line in open(path):
        line = line.strip()
        ret = pattern.match(line)
        if not ret:
            continue
        level = len(ret.groups()[0])
        content = ret.groups()[1].strip()
        if level >= 2:
            summary_structured.append(SummaryStructured('anchor', content, '{}#{}'.format(path, gen_anchor(content)), depth+level-2))
            print 'item: ', level, content


def dfs_dir(current_path, depth=1):
    print 'dfs[{}]: {}'.format(depth, current_path)
    for a, b, c in os.walk(current_path):
        for cc in c:
            if not cc.endswith('.md') and not cc.endswith('.markdown'):
                continue
            if os.path.join(current_path, cc) in ignored:
                continue
            summary_structured.append(SummaryStructured('md', cc, os.path.join(current_path, cc), depth))
            print 'file: '+os.path.join(current_path, cc)
            parse_md(cc, os.path.join(current_path, cc), depth)
        for bb in b:
            if bb.startswith('.'):
                continue
            if os.path.join(current_path, bb) in ignored:
                continue
            summary_structured.append(SummaryStructured('title', bb, os.path.join(current_path, bb), depth))
            dfs_dir(os.path.join(current_path, bb), depth+1)
            print 'dir: '+os.path.join(current_path, bb)
        break


def output_summary(output_file):
    print >>output_file, '# 文档目录'
    for ss in summary_structured:
        if ss.type == 'title':
            print >>output_file, ''
            print >>output_file, '###{} {}'.format('#'*ss.depth, ss.key)
        elif ss.type == 'md':
            key = ss.key.split('.')[0]
            # if not key.endswith('文档'):
                # key += '文档'
            print >>output_file, ''
            # 神特么侧边栏只支持两级列表，只能让文档做第一级，字标题做第二级了
            print >> output_file, '{}* [{}]({})'.format(' ' * 2 * (ss.depth-1), key, ss.path)
            # print >> output_file, '{}* [{}]({})'.format('', key, ss.path)
        elif ss.type == 'anchor':
            # 神特么侧边栏只支持两级列表，只能让文档做第一级，字标题做第二级了
            print >> output_file, '{}* [{}]({})'.format(' ' * 2 * ss.depth, ss.key, ss.path)
            # print >> output_file, '{}* [{}]({})'.format('  ', ss.key, ss.path)
        else:
            error('Unknown type {}.'.format(ss.type))


def main():
    parser = argparse.ArgumentParser(description='SUMMARY.md auto generator for Diachronic Corpus project.')
    parser.add_argument('-f', '--force', help='forced overwrite output file', action='store_true')
    parser.add_argument('-i', '--input', help='input root dir', default='./')
    parser.add_argument('-o', '--output', help='output file name', default='SUMMARY-AUTO.md')

    args = parser.parse_args()
    print 'args:', args

    filename = args.output
    if filename != 'SUMMARY-AUTO.md' and os.path.isfile(filename) and not args.force:
        error('"{}" existed and -f(--force) flag not set.'.format(filename))

    if os.path.isfile('.summary_ignored'):
        ignored.update([line.strip() for line in open('.summary_ignored')])

    print 'ignored: ', ignored
    dfs_dir(args.input)
    output_file = open(filename, 'w')
    output_summary(output_file)


if __name__ == '__main__':
    main()
