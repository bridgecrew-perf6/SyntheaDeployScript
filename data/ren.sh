for file in *\ copy.csv; do
    mv "$file" "${file// copy/}"
done
