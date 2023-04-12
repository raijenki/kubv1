git add .
git commit -m "fix launcher, autoscript"
git push
docker rmi raijenki/mpik8s:cm1
docker build . -t raijenki/mpik8s:cm1
docker push raijenki/mpik8s:cm1
