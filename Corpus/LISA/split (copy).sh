DOCS_INPUT_DIR="$1"
QUERIES_INPUT_DIR="$2"
OUTPUT_DIR="$3"
#EXPLICIT_FILE_NAME="$(pwd)/"$@""
echo $DOCS_INPUT_DIR
echo $QUERIES_INPUT_DIR
echo $OUTPUT_DIR

rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR/docs
mkdir -p $OUTPUT_DIR/queries
#exit(0)
for file in $DOCS_INPUT_DIR/*
do	
    echo $file
    if [[ -f "$file" ]]; then
        echo "processing file...."
	file_name=$(basename $file)
        csplit -z $file /Document/ '{*}' -f $OUTPUT_DIR/docs/$file_name. > /dev/null
        sed -i '/Document/d' $OUTPUT_DIR/docs/$file_name.*
        sed -i '/\*\*\?/d' $OUTPUT_DIR/docs/$file_name.*
    fi
done

for file in $QUERIES_INPUT_DIR/*
do
    echo $file
    if [[ -f "$file" ]]; then
        echo "processing file...."
        file_name=$(basename $file)
        csplit -z $file '/#/+1' '{*}' -f $OUTPUT_DIR/queries/$file_name. > /dev/null
        sed -i '1d' $OUTPUT_DIR/queries/$file_name.*
        sed -i 's|[#]||g' $OUTPUT_DIR/queries/$file_name.*
        #sed -i '/\*\*\?/d' $OUTPUT_DIR/docs/$file_name.*
    fi
done
