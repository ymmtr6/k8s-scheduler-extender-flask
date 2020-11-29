# k8s-scheduler-flask-sample

# RUN

1. build a docker image

```
$ docker build -t account/image:tag .
$ docker push account/image:tag
```

2. deploy custom-scheduler in kube-system namespace

edit extender.yaml


```
$ kubectl apply -f extender.yaml
```

if your debugging

```
$ kubectl -n kube-system logs deploy/custom-scheduler -c custom-scheduler-extender-ctr -f
```

3. scheduler test pod 

```
$ kubectl create -f test-pod.yaml
```
