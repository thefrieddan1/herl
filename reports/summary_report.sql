WITH daily_stats AS (
    SELECT
        machine_code,
        coordinate,
        -- Convert epoch microseconds to date
        strftime(to_timestamp(sample_time / 1000000), '%Y-%m-%d') as sample_date,
        AVG(value) as daily_avg,
        COUNT(*) as samples_cnt
    FROM sensor_readings
    WHERE sample_date IN ('2024-01-01', '2024-01-02')
    GROUP BY machine_code, coordinate, sample_date
),
stats_with_lag AS (
    SELECT
        machine_code,
        coordinate,
        sample_date,
        daily_avg,
        samples_cnt,
        LAG(daily_avg) OVER (PARTITION BY machine_code, coordinate ORDER BY sample_date) as prev_day_avg
    FROM daily_stats
),
increases AS (
    SELECT
        machine_code,
        coordinate,
        daily_avg as value_avg,
        (daily_avg - prev_day_avg) as increase_in_value,
        samples_cnt
    FROM stats_with_lag
    WHERE sample_date = '2024-01-02' AND prev_day_avg IS NOT NULL
),
ranked_increases AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY machine_code ORDER BY increase_in_value DESC) as rn
    FROM increases
)
SELECT
    m.machine_name,
    r.coordinate,
    r.value_avg,
    r.increase_in_value,
    r.samples_cnt
FROM ranked_increases r
LEFT JOIN read_csv_auto('data/Machines.csv') m ON r.machine_code = m.machine_code
WHERE r.rn = 1
ORDER BY r.increase_in_value DESC;
