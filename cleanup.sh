#!/bin/sh

rm *.pyc
rm *.log
mv *.ipynb test/
rm -rf .ipynb_checkpoints
rm *.out

echo 'finish to cleanup analytics directory'
