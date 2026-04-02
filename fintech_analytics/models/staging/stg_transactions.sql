with source as (
    select * from {{ ref('raw_transactions') }}
),

cleaned as (
    select
        transaction_id,
        customer_id,
        cast(transaction_date as date)   as transaction_date,
        transaction_type,
        cast(amount as decimal(10,2))    as amount,
        status,
        product_type,
        date_trunc('month', cast(transaction_date as date)) as transaction_month
    from source
    where status = 'completed'
)

select * from cleaned
