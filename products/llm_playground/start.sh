#!/bin/bash
set -e
obfuscation_only=$OO
encryption_only=$EO
both=$BO

for file_name in $both
  do
    echo "**************obfuscating and encrypting: "$file_name
    obfuscate $file_name
    # Format obfuscated code because sometimes unformatted code gives issues
    black $file_name
    isort $file_name
    # Encrypt obfuscated file to get encrypted .so file
    encrypt $file_name
    # Remove the obfuscated py file
    rm $file_name
done


for file_name in $OO
  do
    echo "**************obfuscating and encrypting: "$file_name
    obfuscate $file_name
    # Do not remove the obfuscated py file
done

