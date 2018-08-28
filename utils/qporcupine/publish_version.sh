
# confirm user updated version number
echo 'PyPi asks that we not push versions too frequently; is this an import
verson, or can it be tested locally? y/N'
read answer
if [ "$answer" != "y" ];
then
  exit 1
fi

# confirm user updated version number
echo 'did you updated the version number in setup.py? y/N'
read answer
if [ "$answer" != "y" ];
then
  exit 1
fi


# confirm necessary tensorflow models are included 
echo 'does your MANIFEST.in have all the necessary tensorflow models in it? y/N'
read answer
if [ "$answer" != "y" ];
then
  exit 1
fi

# move old dist(s) into old_dist folder
mv dist/* old_dist/

# delete old egg
rm -r *.egg-info 

# create new dist
python setup.py bdist_wheel --universal

# upload dist to pypi
twine upload dist/*
