FROM quay.io/coreos/ignition-validate:release AS ignition-validate
FROM alpine:latest as base

ARG CWD_MOUNTDIR
ARG BUILD_DIR
ENV CWD_MOUNTDIR=$CWD_MOUNTDIR
ENV BUILD_DIR=$BUILD_DIR

COPY --from=ignition-validate . .
COPY src/scripts/validate_installs.sh /installs.sh

RUN /installs.sh

CMD $CWD_MOUNTDIR/src/scripts/validate.sh
