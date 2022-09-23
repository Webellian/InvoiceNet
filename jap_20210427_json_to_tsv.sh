echo -n "" > predictions.tsv
for entry in predictions/*.json
do
    line1=`sed -e '2q;d' "$entry"`
    line2=`sed -e '3q;d' "$entry"`
    value_net=`echo $line2 | sed -e 's/^.*: "\(.*\)".*$/\1/g'`
    value_gross=`echo $line1 | sed -e 's/^.*: "\(.*\)".*$/\1/g'`
    echo -e "$entry\t$value_net\t$value_gross" >> predictions.tsv
done
