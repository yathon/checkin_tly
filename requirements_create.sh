#!/usr/bin/env bash

# 安装
# pip3 install pipreqs
# 在当前目录生成
# pipreqs . --encoding=utf8 --force
# 注意 --encoding=utf8 为使用utf8编码，
# 不然可能会报 UnicodeDecodeError: 'gbk' codec can't decode byte
#     0xae in position 406: illegal multibyte sequence 的错误。
# --force 强制执行，当 生成目录下的requirements.txt存在时覆盖。
#
# 使用requirements.txt安装依赖的方式：
# pip3 install -r requirements.txt

PATH_REQS=.
ENCODING=utf8
CMD_PIP=pip
CMD_PIP_REQS=pipreqs
CMD_INSTALL="$CMD_PIP install $CMD_PIP_REQS"
CMD_MAKE_REQS="$CMD_PIP_REQS $PATH_REQS --encoding=$ENCODING --force"

flag=(`$CMD_PIP list | grep $CMD_PIP_REQS | wc -l | sed -e 's/^[ \t]*//g'`)
if [ $flag -ge 1 ]; then
  echo "$CMD_PIP_REQS has installed"
else
  echo "execute command: $CMD_INSTALL"
  `$CMD_INSTALL`
  echo "command finished, $CMD_PIP_REQS installed"
fi

echo "execute command: $CMD_MAKE_REQS"
`$CMD_MAKE_REQS`
echo "command finished."
