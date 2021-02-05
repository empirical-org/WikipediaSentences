INPUTFILE=data/interim/eatingmeat_emma_train_withprompt.ndjson
for LANG in nl de fr es ru zh ko ja
do
    python scripts/create_synthetic_data.py --filename $INPUTFILE --lang $LANG
done
