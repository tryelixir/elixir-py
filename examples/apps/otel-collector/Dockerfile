FROM otel/opentelemetry-collector-contrib:0.100.0

# Copy the configuration file into the container
COPY otel-config.yaml /etc/otel/config.yaml

# Set the working directory
WORKDIR /file-exporter

# Use the default entrypoint provided by the image and provide the config as a command argument
CMD ["--config", "/etc/otel/config.yaml"]
