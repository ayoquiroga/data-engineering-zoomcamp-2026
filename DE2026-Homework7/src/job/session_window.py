from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment


def create_session_sink_postgres(t_env):
    table_name = 'session_trips'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            session_start TIMESTAMP(3),
            session_end   TIMESTAMP(3),
            PULocationID  INTEGER,
            num_trips     BIGINT,
            PRIMARY KEY (session_start, session_end, PULocationID) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
        """
    t_env.execute_sql(sink_ddl)
    return table_name


def create_events_source_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            PULocationID          INTEGER,
            DOLocationID          INTEGER,
            trip_distance         DOUBLE,
            total_amount          DOUBLE,
            lpep_pickup_datetime  BIGINT,
            lpep_dropoff_datetime BIGINT,
            passenger_count       INTEGER,
            tip_amount            DOUBLE,
            event_timestamp AS TO_TIMESTAMP_LTZ(lpep_pickup_datetime, 3),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
        """
    t_env.execute_sql(source_ddl)
    return table_name


def session_window_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)
    env.set_parallelism(1)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    try:
        source_table = create_events_source_kafka(t_env)
        sink_table = create_session_sink_postgres(t_env)

        # Session window: groups events within 5-minute gaps per PULocationID.
        # When no event arrives for a given PULocationID for more than 5 minutes,
        # the window closes and the result is emitted.
        #
        # To find the PULocationID with the longest session after the job runs:
        #   SELECT PULocationID, num_trips, session_start, session_end
        #   FROM session_trips
        #   ORDER BY num_trips DESC
        #   LIMIT 1;
        t_env.execute_sql(f"""
            INSERT INTO {sink_table}
            SELECT
                window_start  AS session_start,
                window_end    AS session_end,
                PULocationID,
                COUNT(*)      AS num_trips
            FROM TABLE(
                SESSION(TABLE {source_table}, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTE)
            )
            GROUP BY window_start, window_end, PULocationID
        """).wait()

    except Exception as e:
        print("Session window job failed:", str(e))


if __name__ == '__main__':
    session_window_job()
