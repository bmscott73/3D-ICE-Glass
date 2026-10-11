FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential bison flex libopenblas-dev csh unzip python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/3d-ice-glass
COPY requirements-analysis.txt .
RUN python3 -m venv /opt/analysis \
    && /opt/analysis/bin/pip install --no-cache-dir -r requirements-analysis.txt
ENV PATH="/opt/analysis/bin:${PATH}"
COPY . .
ARG SUPERLU_U_FILL=100
RUN SUPERLU_U_FILL=${SUPERLU_U_FILL} bash tools/build.sh
ENTRYPOINT ["python3", "tools/run_case.py"]
CMD ["validation/Baselines/H100/ttv_interpack.stk"]
