#from opentelemetry.sdk.metrics import MeterProvider
#from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
#from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Meter Provider einrichten
#metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317/v1/metrics")  # Passe die URL an
#reader = PeriodicExportingMetricReader(metric_exporter)
#meter_provider = MeterProvider(metric_readers=[reader])

# Meter verwenden
#from opentelemetry import metrics
#metrics.set_meter_provider(meter_provider)
#meter = metrics.get_meter(__name__)
#counter = meter.create_counter("example_counter")
#counter.add(1, {"environment": "test"})


from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
import psutil
import time

#---------------------------------------------
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

import grpc

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk import metrics as sdkmetrics
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)



dsn = "http://project1_secret_token@localhost:14318?grpc=14317"
print("using DSN:", dsn)

temporality_delta = {
    sdkmetrics.Counter: AggregationTemporality.DELTA,
    sdkmetrics.UpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.Histogram: AggregationTemporality.DELTA,
    sdkmetrics.ObservableCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableUpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableGauge: AggregationTemporality.DELTA,
}

exporter = OTLPMetricExporter(
    #endpoint="otlp.uptrace.dev:4317",
    endpoint="localhost:4317",insecure=True,

    headers=(("uptrace-dsn", dsn),),
    timeout=5,
    compression=grpc.Compression.Gzip,
    preferred_temporality=temporality_delta,
)
#---------------------------------------------

# Set up a resource for the service emitting the metrics
resource = Resource.create(attributes={
    "service.name": "mycpu-monitoring-service"
})

# Set up the metric exporter and reader (console output)
##ZZ exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=2000)  # 2 seconds interval

# Set the meter provider
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)


# Get a meter from the meter provider
meter = metrics.get_meter("mycpu-meter", "1.0.0")

#ZZ meter = metrics.get_meter_provider().get_meter("cpu-meter")

# Define a callback function to return CPU usage
def get_cpu_usage(callback_options):
    # Obtain the current CPU usage
    cpu_usage = psutil.cpu_percent() * 10
    print(cpu_usage)
    o = metrics.Observation(cpu_usage) 
    #o.value = cpu_usage
    
    # Return the observed value as a list (not a tuple)
    return [o]

# Create an observable gauge using the callback function
meter.create_observable_gauge(
    name="mysystem.cpu.usage",
    description="Reports the current system CPU usage as a percentage on my system",
    unit="%",
    callbacks=[get_cpu_usage]
)

print("Collecting metrics. Press Ctrl+C to stop.")

# Keep the script running to emit metrics at intervals
try:
    while True:
        time.sleep(2)  # Adjust to match the reporting interval as needed
        print("sleeping...")
except KeyboardInterrupt:
    print("Stopped collecting metrics.")
