with transactions as (
    select * from {{ ref('stg_transactions') }}
),

monthly as (
    select
        transaction_month,
        count(distinct customer_id)                         as active_customers,
        count(*)                                            as total_transactions,
        sum(case when transaction_type = 'deposit'
            then amount else 0 end)                         as total_deposits,
        sum(case when transaction_type in ('withdrawal','purchase')
            then amount else 0 end)                         as total_outflows,
        round(avg(amount), 2)                               as avg_transaction_size
    from transactions
    group by transaction_month
    order by transaction_month
)

select * from monthly
