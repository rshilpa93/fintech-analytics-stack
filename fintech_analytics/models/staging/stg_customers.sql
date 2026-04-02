with source as (
    select * from {{ ref('raw_customers') }}
),

cleaned as (
    select
        customer_id,
        first_name || ' ' || last_name  as full_name,
        cast(signup_date as date)        as signup_date,
        plan_type,
        state
    from source
)

select * from cleaned
