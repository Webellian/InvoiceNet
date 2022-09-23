for entry in processed_data/**/*.json
do
    has_payment_term=`grep -c -E "\"payment_term\": \".+\"," "$entry"`
    has_dni_phrase=`grep -c "\"dni\"" "$entry"`
    if ((has_payment_term && !has_dni_phrase)); then
        echo "Removing payment_term from $entry"
        #echo $has_payment_term $has_dni_phrase
        #echo "kill it"
        sed -i -E 's/"payment_term": ".+"/"payment_term": ""/g' "$entry"
    fi
done
