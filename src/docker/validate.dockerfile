FROM quay.io/coreos/ignition-validate:release AS ignition-validate
FROM alpine:latest as base

ARG CWD_MOUNTDIR
ENV CWD_MOUNTDIR=$CWD_MOUNTDIR

COPY --from=ignition-validate . .
COPY scripts/installs.sh /installs.sh

RUN /installs.sh

CMD $CWD_MOUNTDIR/scripts/validate.sh
