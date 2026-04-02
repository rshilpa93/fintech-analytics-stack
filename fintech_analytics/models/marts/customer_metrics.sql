with customers as (
    select * from {{ ref('stg_customers') }}
),

transactions as (
    select * from {{ ref('stg_transactions') }}
),

customer_stats as (
    select
        customer_id,
        count(*)                                    as total_transactions,
        sum(case when transaction_type = 'deposit'
            then amount else 0 end)                 as total_deposits,
        sum(case when transaction_type in ('withdrawal','purchase')
            then amount else 0 end)                 as total_outflows,
        min(transaction_date)                       as first_transaction_date,
        max(transaction_date)                       as last_transaction_date,
        count(distinct transaction_month)           as active_months
    from transactions
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.full_name,
        c.plan_type,
        c.state,
        c.signup_date,
        s.total_transactions,
        s.total_deposits,
        s.total_outflows,
        s.total_deposits - s.total_outflows         as net_balance,
        s.first_transaction_date,
        s.last_transaction_date,
        s.active_months,
        case
            when s.active_months >= 3 then 'high'
            when s.active_months = 2  then 'medium'
            else 'low'
        end                                         as engagement_tier
    from customers c
    left join customer_stats s using (customer_id)
)

select * from final
