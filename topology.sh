#!/bin/sh
set -eu

NAMESPACE="${1:-hassensiad06-dev}"

oc label deployment packet-core vrouter dns telco-supervisor \
  app.kubernetes.io/part-of=telco-monitoring \
  --overwrite -n "$NAMESPACE"

oc label deployment telco-supervisor \
  app.openshift.io/runtime=python \
  --overwrite -n "$NAMESPACE"

oc annotate deployment telco-supervisor \
  'app.openshift.io/connects-to=[{"apiVersion":"apps/v1","kind":"Deployment","name":"packet-core"},{"apiVersion":"apps/v1","kind":"Deployment","name":"vrouter"},{"apiVersion":"apps/v1","kind":"Deployment","name":"dns"}]' \
  --overwrite -n "$NAMESPACE"
