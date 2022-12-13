FROM gitpod/workspace-full-vnc
WORKDIR /workspace/NWEdit
ADD . /workspace/NWEdit
RUN make init-ubuntu