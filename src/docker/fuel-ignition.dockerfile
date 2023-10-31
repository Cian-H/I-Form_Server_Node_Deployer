FROM registry.suse.com/bci/nodejs
ARG CONTAINER_USERID

# Install requirements, create usergroup and add user
RUN zypper -n install --no-recommends mkisofs python3 make gcc gcc-c++
RUN groupadd fuelignition
RUN useradd -m -d /fuelignition fuelignition -u ${CONTAINER_USERID}

COPY --chown=fuelignition . /fuelignition/

USER fuelignition
WORKDIR /fuelignition

RUN npm install

# Run our command
CMD ["npm", "run", "dev"]