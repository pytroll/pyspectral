# Releasing PySpectral

prerequisites: `pip install setuptools twine`


1. checkout master
2. pull from repo
3. run the unittests
4. run `loghub` and update the `CHANGELOG.md` file:

```
loghub pytroll/pyspectral -u <username> -st v0.8.3 -plg bug "Bugs fixed" -plg enhancement "Features added" -plg documentation "Documentation changes"
```

Don't forget to commit!

5. Create a tag with the new version number, starting with a 'v', eg:

```
git tag v0.8.4 -m "Version 0.8.4"
```

See [semver.org](http://semver.org/) on how to write a version number.


6. push changes to github `git push --follow-tags`

7. Verify travis tests passed and deployed sdist and wheel to PyPI
