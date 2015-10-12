#!/bin/bash

#for lange in $(echo ja pt zh uk ca fa sh no ar fi id hu ro cs ko sr ms tr min eo kk da eu bg sk hy he lt hr sl et uz gl nn la vo simple el)
#date='20151002'
date='20150901'
for lange in $(echo de ru it nl pl)
do
    lang=`echo $lange | tr -d '\n'`
    echo $lang
    url="https://dumps.wikimedia.org/"$lang"wiki/"$date"/"$lang"wiki-"$date"-pages-articles.xml.bz2" 
    echo $url
    wget $url
    file=$lang"wiki-"$date"-pages-articles.xml.bz2"
    echo $file
    bunzip2 $file
    mkdir -v ../geo_pages/$lang
done
