#!/usr/bin/env python
# coding: utf-8

# In[18]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")
st.set_page_config(page_title="The Flippening Comparison", layout="wide",initial_sidebar_state="collapsed")


# In[26]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[19]:


st.title('The Flippening comparison between Optimism and Arbitrum')
st.write('')
st.markdown('**Optimism** is a new model of digital democratic governance optimized to drive the rapid and continuous growth of a decentralized ecosystem. The Collective is a group of communities, businesses and citizens united by a mutually beneficial pact to adhere to the maxim that impact = gain; the principle that positive impact for the collective should be rewarded with benefits for the individual. This maxim serves as a purpose, which motivates the creation of a more productive and empathetic economy.')
st.markdown('On the other hand, **Arbitrum** is a Layer 2 Scaling Bridge for Ethereum offering increased security for transactions, asset storage, and more, as well as offering their users the chance to have more control over their digital assets by being decentralized. However, many blockchains are becoming hugely congested, which has led to much slower transaction speeds and, consequently, high gas fees [1](https://phemex.com/academy/what-is-arbitrum).')
st.write('')
st.write('Recently, Optimism and Arbitrum have surpassed Ethereum in combined transaction volume and it is a hard milestone. For this reason, the intention of this app is to understand why this happened and what has been its trajectories by comparing both L2 chains.')
st.write('The following sections have been considered to carry out the analysis:')
st.markdown('1. Activity on Optimism vs Arbitrum')
st.markdown('2. Bridges on Optimism vs Arbitrum')
st.markdown('3. User Profile on Optimism vs Arbitrum')
st.markdown('4. Supply on Optimism vs Arbitrum')
st.write('')
st.subheader('1. Activity on Optimism vs Arbitrum')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Optimism and Arbitrum activity. More specifically, we will analyze the following data:')
st.markdown('● Users netflow')
st.markdown('● USD volume')
st.markdown('● Average USD Volume')
st.markdown('● Total and average transactions')
st.markdown('● Daily number of swaps')
st.markdown('● Total and cumulative users')
st.markdown('● Total and average Fees')
st.write('')

sql="""
with
t1 as (
SELECT date(block_timestamp) as day, COUNT(DISTINCT tx_hash) as total_txs ,
avg(total_txs) over (order by day) as avg_txs
from optimism.core.fact_transactions
where day >= CURRENT_DATE - INTERVAL '3 MONTHS'
GROUP by 1
),
t2 as (
SELECT date(block_timestamp) as day, COUNT(DISTINCT tx_hash) as total_txs ,
avg(total_txs) over (order by day) as avg_txs
from arbitrum.core.fact_transactions
where day >= CURRENT_DATE - INTERVAL '3 MONTHS'
GROUP by 1
)
select 'Optimism' as platform,* from t1 union select 'Arbitrum' as platform,* from t2
"""

@st.cache
results = sdk.query(sql)
df = pd.DataFrame(results.records)
df.info()

with st.expander("Check the analysis"):
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='day:N', y='total_txs:Q',color='platform')
        .properties(title='Daily transactions by platform',width=500))
    
    col2.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='day:N', y='avg_txs:Q',color='platform')
        .properties(title='Daily average transactions per platform',width=500))


    sql="""
    with Prices as (
    select
    date_trunc('day', hour) as Dates,
    avg(price) as Price
    from
    ethereum.core.fact_hourly_token_prices
    where
    symbol = 'WETH'
    group by
    1
    ),
    t1 as (
    select
    date_trunc('day', block_timestamp) as date,
    count (distinct tx_hash) as transactions, count (distinct from_address) as
    users,
    sum (ETH_VALUE * Price) as volume, avg (ETH_VALUE * Price) as
    avg_volume,
    sum (tx_fee * Price) as total_fees, avg (tx_fee * Price) as avg_fees,
    sum(transactions) over (order by date) as total_transactions,
    sum(users) over (order by date) as total_users,
    sum(volume) over (order by date) as total_volume
    from
    optimism.core.fact_transactions
    join Prices on dates = date_trunc('day', block_timestamp)
    where
    block_timestamp >= current_date-INTERVAL '3 MONTHS'
    and status = 'SUCCESS'
    group by 1
    order by 1 desc
    ),
    t2 as (
    select
    date_trunc('day', block_timestamp) as date,
    count (distinct tx_hash) as transactions, count (distinct from_address) as
    users,
    sum (ETH_VALUE * Price) as volume, avg (ETH_VALUE * Price) as
    avg_volume,
    sum (tx_fee * Price) as total_fees, avg (tx_fee * Price) as avg_fees,
    sum(transactions) over (order by date) as total_transactions,
    sum(users) over (order by date) as total_users,
    sum(volume) over (order by date) as total_volume
    from
    arbitrum.core.fact_transactions
    join Prices on dates = date_trunc('day', block_timestamp)
    where
    block_timestamp >= current_date-INTERVAL '3 MONTHS'
    and status = 'SUCCESS'
    group by 1
    order by 1 desc
    )
    select 'Optimism' as platform,* from t1 union select 'Arbitrum' as platform,* from t2

    """
@st.cache
    results = sdk.query(sql)
    df = pd.DataFrame(results.records)
    df.info()

    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='users:Q',color='platform')
        .properties(title='Daily active users by platform',width=500))
        
    col2.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='total_users:Q',color='platform')
        .properties(title='Total active users by platform',width=500))
    
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_area()
        .encode(x='date:N', y='volume:Q',color='platform')
        .properties(title='Daily volume transacted by platform',width=500))
    
    col2.altair_chart(alt.Chart(df)
        .mark_area()
        .encode(x='date:N', y='total_volume:Q',color='platform')
        .properties(title='Total volume transacted by platform',width=500))
    
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='avg_fees:Q',color='platform')
        .properties(title='Daily average transaction fee by platform',width=500))
    
    col2.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='total_fees:Q',color='platform')
        .properties(title='Total fees by platform',width=500))



    sql="""
    with swap_tx as ( select tx_hash
    from optimism.core.fact_event_logs
    where event_name = 'Swap')
    ,
    from_token as ( select
    trunc(block_timestamp,'day') as day, tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS,
    contract_address, raw_amount
    from optimism.core.fact_token_transfers
    where tx_hash in ( select tx_hash from swap_tx) and ORIGIN_FROM_ADDRESS =
    FROM_ADDRESS)
    ,
    to_token as ( select
    trunc(block_timestamp,'day') as day, tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS, contract_address,
    raw_amount
    from optimism.core.fact_token_transfers
    where tx_hash in ( select tx_hash from swap_tx) and ORIGIN_FROM_ADDRESS =
    to_address)
    ,
    labels_in as ( select
    'IN' as status, day,tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS, symbol as token_in, raw_amount as amount_in
    from from_token a join optimism.core.dim_contracts b on a.contract_address = b.address)
    ,
    label_out as ( select
    'out' as status, day, tx_hash , ORIGIN_FROM_ADDRESS, ORIGIN_TO_ADDRESS, symbol
    as token_out, raw_amount as amount_out
    from to_token a join optimism.core.dim_contracts b on a.contract_address = b.address)
    ,
    swap_table as ( select
    DISTINCT a.tx_hash , a.day , a.ORIGIN_FROM_ADDRESS as wallet,
    a.ORIGIN_TO_ADDRESS as platform , a.token_in ,
    b.token_out, a.amount_in, b.amount_out
    from labels_in a left outer join label_out b on a.tx_hash = b.tx_hash and a.day = b.day
    )
    ,
    swap_platform as ( select
    DISTINCT tx_hash , day ,
    case when platform = '0xdef1abe32c034e558cdd535791643c58a13acc10' then '0xProject'
    when platform = '0xe592427a0aece92de3edee1f18e0157c05861564' then 'Uniswap'
    when platform = '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45' then 'Uniswap' end as
    platforms ,
    wallet , token_in , token_out, amount_in, amount_out
    from swap_table
    where platforms is not null
    and day >= current_date - INTERVAL '3 MONTHS'
    )
    ,
    price as ( select trunc(hour,'day') as day, symbol, decimals, avg(price) as token_price
    from optimism.core.fact_hourly_token_prices
    where hour::date >= current_date - INTERVAL '3 MONTHS'
    group by 1,2,3)
    ,
    swap_platforms as (select a.day, wallet, tx_hash, platforms, token_in,
    amount_in/pow(10,b.decimals)*b.token_price as amount_from, token_out,
    amount_out/pow(10,c.decimals)*c.token_price as amount_to
    from swap_platform a left outer join price b on a.day = b.day and a.token_in = b.symbol
    left outer join price c on a.day = c.day and a.token_out = c.symbol
    where token_in is not null and
    token_out is not null
    UNION
    select trunc(block_timestamp,'day') as day,
    origin_from_address as wallet,
    tx_hash,
    'Velodrome' as platforms, symbol_in as token_in, amount_in_usd as amount_from,
    symbol_out as token_out, amount_out_usd as amount_to
    from optimism.velodrome.ez_swaps
    where block_timestamp::date >= current_date - INTERVAL '3 MONTHS'
    UNION
    select trunc(block_timestamp,'day') as day,
    origin_from_address as wallet,
    tx_hash, 'Sushiswap' as platfroms, symbol_in as token_in,
    amount_in_usd as amount_from, symbol_out as token_out, amount_out_usd as amount_to
    from optimism.sushi.ez_swaps
    where block_timestamp::date >= current_date - INTERVAL '3 MONTHS'),
    optimism as (
    select day,
    count(DISTINCT tx_hash) as swaps, count(DISTINCT wallet) as users, sum(amount_from)
    as volume_usd, avg(amount_from) as average_volume
    from swap_platforms
    group by 1
    ),
    swap_tx2 as ( select tx_hash
    from arbitrum.core.fact_event_logs
    where event_name = 'Swap')
    ,
    from_token_2 as ( select
    trunc(block_timestamp,'day') as day, tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS,
    contract_address, raw_amount
    from arbitrum.core.fact_token_transfers
    where tx_hash in ( select tx_hash from swap_tx2) and ORIGIN_FROM_ADDRESS =
    FROM_ADDRESS)
    ,
    to_token_2 as ( select
    trunc(block_timestamp,'day') as day, tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS, contract_address,
    raw_amount
    from arbitrum.core.fact_token_transfers
    where tx_hash in ( select tx_hash from swap_tx2) and ORIGIN_FROM_ADDRESS =
    to_address)
    ,
    labels_in_2 as ( select
    'IN' as status, day,tx_hash, ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS, symbol as token_in, raw_amount as amount_in
    from from_token_2 a join arbitrum.core.dim_contracts b on a.contract_address = b.address)
    ,
    label_out_2 as ( select
    'out' as status, day, tx_hash , ORIGIN_FROM_ADDRESS, ORIGIN_TO_ADDRESS, symbol
    as token_out, raw_amount as amount_out
    from to_token_2 a join arbitrum.core.dim_contracts b on a.contract_address = b.address)
    ,
    swap_table2 as ( select
    DISTINCT a.tx_hash , a.day , a.ORIGIN_FROM_ADDRESS as wallet,
    a.ORIGIN_TO_ADDRESS as platform , a.token_in ,
    b.token_out, a.amount_in, b.amount_out
    from labels_in_2 a left outer join label_out_2 b on a.tx_hash = b.tx_hash and a.day = b.day
    )
    ,
    swap_platform2 as ( select
    DISTINCT tx_hash , day ,
    case when platform = '0xdef1abe32c034e558cdd535791643c58a13acc10' then '0xProject'
    when platform = '0xe592427a0aece92de3edee1f18e0157c05861564' then 'Uniswap'
    when platform = '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45' then 'Uniswap' end as
    platforms ,
    wallet , token_in , token_out, amount_in, amount_out
    from swap_table2
    where platforms is not null
    and day >= current_date - INTERVAL '3 MONTHS'
    )
    ,
    price2 as ( select trunc(hour,'day') as day, symbol, decimals, avg(price) as token_price
    from ethereum.core.fact_hourly_token_prices
    where hour::date >= current_date - INTERVAL '3 MONTHS'
    group by 1,2,3)
    ,
    swap_platform2s as (select a.day, wallet, tx_hash, platforms, token_in,
    amount_in/pow(10,b.decimals)*b.token_price as amount_from, token_out,
    amount_out/pow(10,c.decimals)*c.token_price as amount_to
    from swap_platform2 a left outer join price b on a.day = b.day and a.token_in = b.symbol
    left outer join price2 c on a.day = c.day and a.token_out = c.symbol
    where token_in is not null and
    token_out is not null
    UNION
    select trunc(block_timestamp,'day') as day,
    origin_from_address as wallet,
    tx_hash, 'Sushiswap' as platfroms, symbol_in as token_in,
    amount_in_usd as amount_from, symbol_out as token_out, amount_out_usd as amount_to
    from arbitrum.sushi.ez_swaps
    where block_timestamp::date >= current_date - INTERVAL '3 MONTHS'),
    arbitrum as (
    select day,
    count(DISTINCT tx_hash) as swaps, count(DISTINCT wallet) as users, sum(amount_from)
    as volume_usd, avg(amount_from) as average_volume
    from swap_platform2s
    group by 1
    )
    select 'Optimism' as platform,* from optimism union select 'Arbitrum' as platform,* from arbitrum
    """
@st.cache
    results = sdk.query(sql)
    df = pd.DataFrame(results.records)
    df.info()

    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='swaps:Q',color='platform')
    .properties(title='Daily swaps by platform',width=1000))
    
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='users:Q',color='platform')
    .properties(title='Daily swappers by platform',width=1000))
    
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='volume_usd:Q',color='platform')
    .properties(title='Daily volume swapped (USD) by platform',width=1000))
    
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='users:Q',color='platform')
    .properties(title='Daily average volume (USD) by platform',width=1000))



# In[20]:

st.write('')
st.markdown('First of all we can see that during the last three months we can see that the two platforms have had a fairly stable daily transactions but always with an upward trend. Both have had a rise in January. Arbitrum has a higher transaction total than Optimism.')
st.markdown('If we look at the daily active users we can see that Optimism has had an upward trend, while Arbitrum has had the opposite. At the end of December Optimism overtook Arbitrum in the number of active users.')
st.markdown('In the daily volume transacted we see that Arbitrum has a higher total volume than Optimism. Even so, they have very similar trends, when one goes up, so does the other.')
st.markdown('Finally, we can see that in the number of swappers, Optimism outperformed Arbitrum at the end of December. The two platforms have very similar figures in terms of volume swapped.')
st.write('')
st.subheader("2. Bridges on Optimism vs Arbitrum")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Optimism and Arbitrum bridges. More specifically, we will analyze the following data:')
st.markdown('● Unique bridges')
st.markdown('● Volume bridged')
st.markdown('● Average volume bridged')

sql="""
with hop AS (select A.BLOCK_TIMESTAMP AS BLOCK_TIMESTAMP,A.TX_HASH AS
TX_HASH,A.ORIGIN_FROM_ADDRESS AS bridger,
case when A.ORIGIN_TO_ADDRESS='0x3d4cc8a61c7528fd86c55cfe061a78dcba48edd1'
then 'DAI'
when A.ORIGIN_TO_ADDRESS='0xb8901acb165ed027e32754e0ffe830802919727f' then
'ETH'
when A.ORIGIN_TO_ADDRESS='0x22b1cbb8d98a01a3b71d034bb899775a76eb1cc2'
then 'MATIC'
when A.ORIGIN_TO_ADDRESS='0x3666f603cc164936c1b87e207f36beba4ac5f18a' then
'USDC'
when A.ORIGIN_TO_ADDRESS='0x3e4a3a4796d16c0cd582c382691998f7c06420b6' then
'USDT'
when A.ORIGIN_TO_ADDRESS='0xb98454270065a31d71bf635f6f7ee6a518dfb849' then
'WBTC'
end AS SYMBOL,
AMOUNT,
AMOUNT_USD
from ethereum.core.fact_event_logs A inner join ethereum.core.ez_token_transfers B on
A.TX_HASH=B.TX_HASH
where EVENT_NAME='TransferSentToL2' and EVENT_INPUTS:chainId='10' and
TX_STATUS='SUCCESS'
and A.ORIGIN_TO_ADDRESS in
('0x3d4cc8a61c7528fd86c55cfe061a78dcba48edd1','0xb8901acb165ed027e32754e0ffe830
802919727f'
,'0x22b1cbb8d98a01a3b71d034bb899775a76eb1cc2','0x3666f603cc164936c1b87e207f36b
eba4ac5f18a','0x3e4a3a4796d16c0cd582c382691998f7c06420b6',
'0xb98454270065a31d71bf635f6f7ee6a518dfb849')
union ALL
select A.BLOCK_TIMESTAMP AS BLOCK_TIMESTAMP,A.TX_HASH AS
TX_HASH,A.ORIGIN_FROM_ADDRESS AS bridger,
case when A.ORIGIN_TO_ADDRESS='0x3d4cc8a61c7528fd86c55cfe061a78dcba48edd1'
then 'DAI'
when A.ORIGIN_TO_ADDRESS='0xb8901acb165ed027e32754e0ffe830802919727f' then
'ETH'
when A.ORIGIN_TO_ADDRESS='0x22b1cbb8d98a01a3b71d034bb899775a76eb1cc2'
then 'MATIC'
when A.ORIGIN_TO_ADDRESS='0x3666f603cc164936c1b87e207f36beba4ac5f18a' then
'USDC'
when A.ORIGIN_TO_ADDRESS='0x3e4a3a4796d16c0cd582c382691998f7c06420b6' then
'USDT'
when A.ORIGIN_TO_ADDRESS='0xb98454270065a31d71bf635f6f7ee6a518dfb849' then
'WBTC'
end AS SYMBOL,
AMOUNT,
AMOUNT_USD
from ethereum.core.fact_event_logs A inner join ethereum.core.ez_eth_transfers B on
A.TX_HASH=B.TX_HASH
where EVENT_NAME='TransferSentToL2' and EVENT_INPUTS:chainId='10' and
TX_STATUS='SUCCESS'
and A.ORIGIN_TO_ADDRESS in
('0x3d4cc8a61c7528fd86c55cfe061a78dcba48edd1','0xb8901acb165ed027e32754e0ffe830
802919727f'
,'0x22b1cbb8d98a01a3b71d034bb899775a76eb1cc2','0x3666f603cc164936c1b87e207f36b
eba4ac5f18a','0x3e4a3a4796d16c0cd582c382691998f7c06420b6',
'0xb98454270065a31d71bf635f6f7ee6a518dfb849')),
hop2 AS (
select A.BLOCK_TIMESTAMP,A.TX_HASH AS TX_HASH,A.ORIGIN_FROM_ADDRESS
AS bridger,case when SYMBOL='WETH' then 'ETH'
else SYMBOL end AS SYMBOL,raw_amount*power(10,-DECIMALS) AS
amount,raw_amount*power(10,-DECIMALS)*price AS amount_USD
from optimism.core.fact_event_logs A inner join optimism.core.fact_token_transfers B on
A.TX_HASH=B.TX_HASH
inner join optimism.core.fact_hourly_token_prices C on
B.CONTRACT_ADDRESS=C.TOKEN_ADDRESS and
date_trunc('hour',A.BLOCK_TIMESTAMP)=C.HOUR
where A.ORIGIN_TO_ADDRESS in
('0x86ca30bef97fb651b8d866d45503684b90cb3312',lower('0x2ad09850b0CA4c7c1B33f5Ac
D6cBAbCaB5d6e796')
,lower('0x7D269D3E0d61A05a0bA976b7DBF8805bF844AF3F'),lower('0xb3C68a491608952
Cb1257FC9909a537a0173b63B'),lower('0x2A11a98e2fCF4674F30934B5166645fE6CA35F
56'),lower('0xf11EBB94EC986EA891Aec29cfF151345C83b33Ec'))
and EVENT_NAME is NULL and
TOPICS[2]='0x0000000000000000000000000000000000000000000000000000000000000
001'
),
cbridge AS (
select A.BLOCK_TIMESTAMP AS BLOCK_TIMESTAMP,A.TX_HASH AS
TX_HASH,A.ORIGIN_FROM_ADDRESS AS bridger,symbol,amount,amount_usd
from ethereum.core.fact_event_logs A inner join ethereum.core.ez_token_transfers B on
A.TX_HASH=B.TX_HASH
where A.ORIGIN_TO_ADDRESS='0x5427fefa711eff984124bfbb1ab6fbf5e3da1820' and
CONTRACT_NAME='Bridge' and tokenflow_eth.hextoint(substr(data,385,2))=10
union ALL
select A.BLOCK_TIMESTAMP AS BLOCK_TIMESTAMP,A.TX_HASH AS
TX_HASH,A.ORIGIN_FROM_ADDRESS AS bridger,'ETH' AS symbol,amount,amount_usd
from ethereum.core.fact_event_logs A inner join ethereum.core.ez_eth_transfers B on
A.TX_HASH=B.TX_HASH
where A.ORIGIN_TO_ADDRESS='0x5427fefa711eff984124bfbb1ab6fbf5e3da1820' and
CONTRACT_NAME='Bridge' and tokenflow_eth.hextoint(substr(data,385,2))=10),
cbridge2 AS (
select A.BLOCK_TIMESTAMP,A.TX_HASH AS TX_HASH,A.ORIGIN_FROM_ADDRESS AS
bridger,case when SYMBOL='WETH' then 'ETH'
else SYMBOL end AS SYMBOL,raw_amount*power(10,-DECIMALS) AS
amount,raw_amount*power(10,-DECIMALS)*price AS amount_USD
from optimism.core.fact_event_logs A inner join optimism.core.fact_token_transfers B on
A.TX_HASH=B.TX_HASH
inner join optimism.core.fact_hourly_token_prices C on
B.CONTRACT_ADDRESS=C.TOKEN_ADDRESS and
date_trunc('hour',A.BLOCK_TIMESTAMP)=C.HOUR
where A.ORIGIN_TO_ADDRESS='0x9d39fc627a6d9d9f8c831c16995b209548cc3401'
and EVENT_NAME='Send' and EVENT_INPUTS:dstChainId='1'
),
main AS (
select
BLOCK_TIMESTAMP,
TX_HASH,
ORIGIN_FROM_ADDRESS AS bridger,
'ETH' AS symbol,
amount,amount_usd
from ethereum.core.ez_eth_transfers
where ETH_TO_ADDRESS in
('0x99c9fc46f92e8a1c0dec1b1747d010903e884be1','0x52ec2f3d7c5977a8e558c8d9c6000b
615098e8fc') and amount_usd is not NULL and symbol is not null
union ALL
select
BLOCK_TIMESTAMP,
TX_HASH,
ORIGIN_FROM_ADDRESS AS bridger,
symbol,
amount,amount_usd
from ethereum.core.ez_token_transfers
where TO_ADDRESS in
('0x99c9fc46f92e8a1c0dec1b1747d010903e884be1','0x52ec2f3d7c5977a8e558c8d9c6000b
615098e8fc') and amount_usd is not NULL and symbol is not null),
main2 AS (
select
BLOCK_TIMESTAMP,
TX_HASH,
ORIGIN_FROM_ADDRESS AS bridger,
'ETH' AS symbol,
amount,amount_usd
from ethereum.core.ez_eth_transfers
where ETH_from_ADDRESS in
('0x99c9fc46f92e8a1c0dec1b1747d010903e884be1','0x52ec2f3d7c5977a8e558c8d9c6000b
615098e8fc')
union ALL
select
BLOCK_TIMESTAMP,
TX_HASH,
ORIGIN_FROM_ADDRESS AS bridger,
symbol,
amount,amount_usd
from ethereum.core.ez_token_transfers
where from_ADDRESS in
('0x99c9fc46f92e8a1c0dec1b1747d010903e884be1','0x52ec2f3d7c5977a8e558c8d9c6000b
615098e8fc')
),
tb AS (select 'hop' AS bridge,'Ethereum' AS origchain,'optimism' AS destchain,* from hop
union ALL
select 'hop' AS bridge,'optimism' AS origchain,'Ethereum' AS destchain,* from hop2
union ALL
select 'cbridgeV2' AS bridge,'Ethereum' AS origchain,'optimism' AS destchain,* from cbridge
union ALL
select 'cbridgeV2' AS bridge,'optimism' AS origchain,'Ethereum' AS destchain,* from
cbridge2
union ALL
select 'main bridge' AS bridge,'Ethereum' AS origchain,'optimism' AS destchain,* from main
union ALL
select 'main bridge' AS bridge,'optimism' AS origchain,'Ethereum' AS destchain,* from
main2),
optimism as (
select
date_trunc('day',BLOCK_TIMESTAMP) AS day,
sum(amount_usd) AS volume,
count(distinct tx_hash) AS unique_bridges,
avg(amount_usd) AS average_bridged_amount
from tb where date_trunc('day',BLOCK_TIMESTAMP) >=current_date-INTERVAL '3 MONTHS' and destchain='optimism'
group by 1
),

  token_contract as (
  	select * from arbitrum.core.dim_labels where address = lower('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1')
  ),
  celer_bridges as (
    -- NOTE for Celer Network: to_address = cBridge means transfer out (dest_chain id observed in input_data)
    -- Transfer ETH from other chain to Arbitrum
    select 
      'Celer Network' as bridge, block_number, block_timestamp,
      tx_hash, raw_amount/pow(10,18) as amount_weth
    from arbitrum.core.fact_token_transfers 
    where 1=1
      and contract_address in (select address from token_contract) -- 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 -- WETH
      and origin_to_address = lower('0x1619de6b6b20ed217a58d00f37b9d47c7663feca') -- Celer Network: cBridge
      and to_address <> '0x1619de6b6b20ed217a58d00f37b9d47c7663feca'
  	  and origin_function_signature = '0xcdd1b25d' -- relay id
  ),
  celer_with_src_chain as (
  	select 
  		bridges.*,
  		regexp_substr_all(SUBSTR(fta.tx_json:receipt:logs[1]:data, 3, len(fta.tx_json:receipt:logs[1]:data)), '.{64}') AS segmented_data, 
  		ethereum.public.udf_hex_to_int(segmented_data[5]) as src_chain_id 
  	from arbitrum.core.fact_transactions  fta 
  		right join celer_bridges bridges on (bridges.tx_hash = fta.tx_hash and bridges.bridge = 'Celer Network')
  	),
  across_bridges as (
  	-- NOTE for Across Protocol: multicall contract + dest_chain id observed in input_data, so take it as deposit into arbitrum
	select 
	  'Across' as bridge, block_number, block_timestamp,
	  tx_hash, raw_amount/pow(10,18) as amount_weth
	from arbitrum.core.fact_token_transfers 
	where 1=1
	  and contract_address in (select address from token_contract) -- 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 -- WETH
	  and to_address = lower('0xb88690461ddbab6f04dfad7df66b7725942feb9c') -- Across Protocol: Arbitrum Spoke Pool V2
	  and from_address <> '0x0000000000000000000000000000000000000000'
	  and origin_function_signature not in ('0x49228978', '0xa44bbb15') -- deposit (bridge out)
   ),
  across_with_src_chain as (
  	select
  	  'Across' as bridge, block_number, block_timestamp,
	  tx_hash,
	  regexp_substr_all(SUBSTR(data, 3, len(data)), '.{64}') AS segmented_data, 
	  try_to_number(ethereum.public.udf_hex_to_int(segmented_data[1]))/pow(10,18) as amount_weth, 
	  ethereum.public.udf_hex_to_int(segmented_data[4]) as src_chain_id,
  	  concat('0x', substr(segmented_data[10], -40, 40)) as denom
  	from arbitrum.core.fact_event_logs
  	where tx_hash in (select distinct tx_hash from across_bridges where bridge = 'Across')
  	having amount_weth is not null
  ),
  hop_with_src_chain as (
  	select 
	  'Hop' as bridge, block_number, block_timestamp,
	  tx_hash, raw_amount/pow(10,18) as amount_weth,
	  iff(origin_function_signature = '0xcc29a306', '1', null) as src_chain_id
	from arbitrum.core.fact_token_transfers 
	where 1=1
	  and contract_address in (lower('0xDa7c0de432a9346bB6e96aC74e3B61A36d8a77eB')) -- hETH
	  -- and origin_from_address = lower('0x710bDa329b2a6224E4B44833DE30F38E7f81d564') -- Hop Protocol: ETH Bonder
	  and origin_function_signature in ('0x3d12a85a', '0xcc29a306') -- bondWithdrawalAndDistribute (inbound)/TransferFromL1Completed (inbound from L1)
	  and to_address = origin_to_address
  ),
   multichain_bridges as (
  	-- NOTE for Multichain Protocol: anySwapInAuto (Inbound), there's fromChainID in inputs_data. hence, consider them as deposit into arbitrum
	select 
	  'Multichain' as bridge, block_number, block_timestamp,
	  tx_hash, raw_amount/pow(10,18) as amount_weth
	from arbitrum.core.fact_token_transfers
	where 1=1
	  and contract_address in (lower('0x1dd9e9e142f3f84d90af1a9f2cb617c7e08420a4')) -- anyWETH
	  and origin_to_address = lower('0x650af55d5877f289837c30b94af91538a7504b76') -- multichain
	  and origin_function_signature = '0x0175b1c4' -- anySwapInAuto (Inbound), there's fromChainID in inputs_data
	  and from_address = '0x0000000000000000000000000000000000000000'
  ),
  multichain_with_src_chain as (
  	select 
  		bridges.*,
  		regexp_substr_all(SUBSTR(input_data, 11, len(input_data)), '.{64}') AS segmented_data, 
  		ethereum.public.udf_hex_to_int(segmented_data[4]) as src_chain_id
  	from arbitrum.core.fact_transactions  fta 
  		right join multichain_bridges bridges on (bridges.tx_hash = fta.tx_hash and bridges.bridge = 'Multichain')
  ),
  bungee_with_src_chain as (
  	select
	  'Bungee' as bridge, block_number, block_timestamp,
	  tx_hash, event_inputs:amount/pow(10,18) as amount_weth,
	  '1' as src_chain_id
	from ethereum.core.fact_event_logs 
	where 1=1
	  and event_inputs:chainId::string = '42161'
	  and origin_to_address = lower('0xc30141b657f4216252dc59af2e7cdb9d8792e1b0')
	  and tx_hash in (select distinct tx_hash from ethereum.core.ez_eth_transfers where origin_to_address = lower('0xc30141b657f4216252dc59af2e7cdb9d8792e1b0'))
  ),
  debridge_with_src_chain as (
  	select 
  		'Debridge' as bridge,
      tx_hash, block_number, block_timestamp, regexp_substr_all(SUBSTR(input_data, 11, len(input_data)), '.{64}') AS segmented_data,
      ethereum.public.udf_hex_to_int(segmented_data[2]) as src_chain_id,
      try_to_number(ethereum.public.udf_hex_to_int(segmented_data[1]))/pow(10,18) as amount_weth
    from arbitrum.core.fact_transactions
    where 1=1
      and tx_hash in (select distinct tx_hash from arbitrum.core.fact_event_logs where origin_to_address = lower('0x43de2d77bf8027e25dbd179b491e8d64f38398aa') and origin_function_signature = '0xc280c905' and contract_address = lower('0xcAB86F6Fb6d1C2cBeeB97854A0C023446A075Fe3'))
      and origin_function_signature = '0xc280c905'
  ),
  bridge_wrapper as (
	select 
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from celer_with_src_chain
	union all 
	select 
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from multichain_with_src_chain
	union all 
	select
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from across_with_src_chain
  	where denom = lower('0x82af49447d8a07e3bd95bd0d56f35241523fbab1') -- weth
	union all 
	select 
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from hop_with_src_chain
	union all 
	select 
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from bungee_with_src_chain
	union all 
	select 
		bridge, block_number, block_timestamp,
		tx_hash, src_chain_id, amount_weth
	from debridge_with_src_chain
  ),
  eth_price as (
  select
  date_trunc('day',hour) as day,
  avg(price) as price
  from ethereum.core.fact_hourly_token_prices where symbol='WETH'
  group by 1
  ),
  final_bridge as (
  select
 trunc(block_timestamp,'day') as day,
 count(tx_hash) as unique_bridges,
 sum(amount_weth) as volumes,
     avg(amount_weth) AS average_bridged_amounts
     from bridge_wrapper where block_timestamp>=current_date-INTERVAL '3 MONTHS'
--     and src_chain_id='Ethereum'
     group by 1
  ),
  arbitrum as (
	 select 
	 	x.day,
	 	volumes*price as volume,
  	 	unique_bridges,
    average_bridged_amounts*price AS average_bridged_amount
	 from final_bridge x
     join eth_price y on x.day=y.day
 )
  select 'Optimism' as platform,* from optimism union select 'Arbitrum' as platform,* from arbitrum
"""
@st.cache
results = sdk.query(sql)
df = pd.DataFrame(results.records)
df.info()

with st.expander("Check the analysis"):
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='volume:Q',color='platform')
    .properties(title='Daily volume bridged (USD) by platform',width=1000))
    
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='unique_bridges:Q',color='platform')
    .properties(title='Daily bridges by platform',width=1000))
    
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='day:N', y='average_bridged_amount:Q',color='platform')
    .properties(title='Daily average volume bridged (USD) by platform',width=1000))
    


# In[21]:

st.write('')
st.markdown('If we look at the daily volume bridged we see that the Optimism platform has more ups and downs. Arbitrum, on the other hand, has a more stable volume bridged. They have very similar values. In the bridges we see that Arbitrum increased dramatically in mid-November but then dropped sharply and now Optimism and Arbitrum have the same values. Finally, in the average volume bridged, we can see that in the first month, Optimism had higher values than the other platform. Even so, it has shown much more ups and downs. Arbitrum has remained stable over the three months. They have similar values although Ooptimism has a slightly higher average volume bridged.  ')
st.markdown('')
st.write('')
st.subheader("3. User profile comparison")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Optimism and Arbitrum user profile. More specifically, we will analyze the following data:')
st.markdown('● Number of transactions by actions')
st.markdown('● Current number of transactions by actions')
st.markdown('● Distribution percentage of actions')
st.markdown('● Number of transactions by sectors')
st.markdown('● Current number of transactions by sectors')
st.markdown('● Distribution percentage of sectors')
st.markdown('● Type of transactions per user activity')

sql="""
with
optimism as (
SELECT
date_trunc('day', block_timestamp) as date,
CASE
WHEN tx_hash IN (SELECT DISTINCT tx_hash from optimism.core.ez_nft_sales) THEN
'NFT'
WHEN event_name IN ('Swap', 'TokenExchange', 'Swapped') THEN 'Swap'
WHEN event_name ilike '%Delegate%' THEN 'Delegate'
WHEN (event_name ilike '%liquidity%' OR event_name ilike '%farm%') AND
event_name ilike '%Liquidity%' THEN 'Farming and Liquidity'
WHEN event_name ilike '%Stake%' THEN 'Stake'
WHEN event_name ilike '%layer2%' THEN 'Bridging activities'
WHEN event_name ilike '%Perpetual Protocol%' THEN 'Leveraged Positions'
ELSE 'Other'
END as type,
COUNT(DISTINCT tx_hash) as transactions
FROM optimism.core.fact_event_logs
WHERE type is not null and block_timestamp >= '2023-01-01'
GROUP BY 1,2
)
select * from optimism
"""

sql2="""
with
arbitrum as (
SELECT
date_trunc('day', block_timestamp) as date,
CASE
WHEN event_name ilike '%nft%' THEN
'NFT'
WHEN event_name IN ('Swap', 'TokenExchange', 'Swapped') THEN 'Swap'
WHEN event_name ilike '%Delegate%' THEN 'Delegate'
WHEN (event_name ilike '%liquidity%' OR event_name ilike '%farm%') AND
event_name ilike '%Liquidity%' THEN 'Farming and Liquidity'
WHEN event_name ilike '%Stake%' THEN 'Stake'
WHEN event_name ilike '%layer2%' THEN 'Bridging activities'
WHEN event_name ilike '%Perpetual Protocol%' THEN 'Leveraged Positions'
ELSE 'Other'
END as type,
COUNT(DISTINCT tx_hash) as transactions
FROM arbitrum.core.fact_event_logs
WHERE type is not null and block_timestamp >= '2023-01-01'
GROUP BY 1,2
)
select * from arbitrum
"""
@st.cache
results = sdk.query(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = sdk.query(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='transactions:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
        .properties(title='Number of transactions by actions on Optimism',width=500))

    col2.altair_chart(alt.Chart(df2)
    .mark_line()
    .encode(x='date:N', y='transactions:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
    .properties(title='Number of transactions by actions on Arbitrum',width=500))

    sql="""
    with
    optimism as (
    SELECT
    date_trunc('day', block_timestamp) as date,
    INITCAP(l.LABEL_TYPE) as type,
    COUNT(DISTINCT ORIGIN_FROM_ADDRESS) as users,
    COUNT(DISTINCT tx_hash) as transactions
    FROM optimism.core.fact_event_logs
    JOIN optimism.core.dim_labels l ON ADDRESS = ORIGIN_TO_ADDRESS
    WHERE
    TX_STATUS = 'SUCCESS'
    AND block_timestamp >= '2023-01-01'
    GROUP BY 1, 2
    ORDER BY 1, 2
    )
    select * from optimism
    """

    sql2="""
    with
    arbitrum as (
    SELECT
    date_trunc('day', block_timestamp) as date,
    INITCAP(l.LABEL_TYPE) as type,
    COUNT(DISTINCT ORIGIN_FROM_ADDRESS) as users,
    COUNT(DISTINCT tx_hash) as transactions
    FROM arbitrum.core.fact_event_logs
    JOIN arbitrum.core.dim_labels l ON ADDRESS = ORIGIN_TO_ADDRESS
    WHERE
    TX_STATUS = 'SUCCESS'
    AND block_timestamp >= '2023-01-01'
    GROUP BY 1, 2
    ORDER BY 1, 2
    )
    select * from arbitrum
    """
@st.cache
    results = sdk.query(sql)
    df = pd.DataFrame(results.records)
    df.info()
    
    results2 = sdk.query(sql2)
    df2 = pd.DataFrame(results2.records)
    df2.info()

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='transactions:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
        .properties(title='Number of transactions by sector on Optimism',width=500))

    col2.altair_chart(alt.Chart(df2)
    .mark_line()
    .encode(x='date:N', y='transactions:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
    .properties(title='Number of transactions by sector on Arbitrum',width=500))

    sql="""
    WITH
    act as (
    SELECT
    ORIGIN_FROM_ADDRESS as Wallet,
    INITCAP(l.LABEL_TYPE) as type,
    COUNT(tx_hash) as transactions
    FROM optimism.core.fact_event_logs
    JOIN optimism.core.dim_labels l ON ADDRESS = ORIGIN_TO_ADDRESS
    WHERE
    TX_STATUS = 'SUCCESS'
    GROUP BY 1, 2
    ORDER BY 1, 2
    )
    SELECT
    CASE
    WHEN transactions BETWEEN 0 AND 5 THEN 'a. <5'
    WHEN transactions BETWEEN 5 AND 50 THEN 'b. 5-50'
    WHEN transactions BETWEEN 50 AND 500 THEN 'c. 50-500'
    WHEN transactions BETWEEN 500 AND 1000 THEN 'd. 500-1000'
    else 'e. >1000'
    END as status,
    type,
    COUNT(Wallet) as counts
    FROM act
    GROUP BY 1,2
    ORDER by 1
    """
    
    sql2="""
    WITH
    act as (
    SELECT
    ORIGIN_FROM_ADDRESS as Wallet,
    INITCAP(l.LABEL_TYPE) as type,
    COUNT(tx_hash) as transactions
    FROM arbitrum.core.fact_event_logs
    JOIN arbitrum.core.dim_labels l ON ADDRESS = ORIGIN_TO_ADDRESS
    WHERE
    TX_STATUS = 'SUCCESS'
    GROUP BY 1, 2
    ORDER BY 1, 2
    )
    SELECT
    CASE
    WHEN transactions BETWEEN 0 AND 5 THEN 'a. <5'
    WHEN transactions BETWEEN 5 AND 50 THEN 'b. 5-50'
    WHEN transactions BETWEEN 50 AND 500 THEN 'c. 50-500'
    WHEN transactions BETWEEN 500 AND 1000 THEN 'd. 500-1000'
    else 'e. >1000'
    END as status,
    type,
    COUNT(Wallet) as counts
    FROM act
    GROUP BY 1,2
    ORDER by 1
    """
@st.cache
    results = sdk.query(sql)
    df = pd.DataFrame(results.records)
    df.info()
    
    results2 = sdk.query(sql2)
    df2 = pd.DataFrame(results2.records)
    df2.info()

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='status:N', y='counts:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
        .properties(title='Distribution of transactions by sector on Optimism',width=500))

    col2.altair_chart(alt.Chart(df2)
    .mark_line()
    .encode(x='status:N', y='counts:Q',color=alt.Color('type', scale=alt.Scale(scheme='dark2')))
    .properties(title='Distribution of transactions by sector on Arbitrum',width=500))

st.write('')
st.markdown('Finally, we have analysed the user profile comparison. In Optimism, in the number of transactions by actions we see that Other is the most used option, just like in the Arbitrum platform. In the number of transactions by sector we see that in Optimism Layer2 is the most used, while in Arbitrum Dex and Layer2 are the most used. ')
st.write('')
st.subheader('Conclusions')
st.markdown('During the last three months we can see that the two platforms have had a fairly stable daily transactions but always with an upward trend. Both have had a rise in January. Arbitrum has a higher transaction total than Optimism. The daily active users we can see that Optimism has had an upward trend, while Arbitrum has had the opposite. At the end of December Optimism overtook Arbitrum in the number of active users. In the daily volume transacted we see that Arbitrum has a higher total volume than Optimism. Even so, they have very similar trends, when one goes up, so does the other. Finally, we can see that in the number of swappers, Optimism outperformed Arbitrum at the end of December. The two platforms have very similar figures in terms of volume swapped.')
st.markdown('If we look at the daily volume bridged we see that the Optimism platform has more ups and downs. Arbitrum, on the other hand, has a more stable volume bridged. They have very similar values. In the bridges we see that Arbitrum increased dramatically in mid-November but then dropped sharply and now Optimism and Arbitrum have the same values. Finally, in the average volume bridged, we can see that in the first month, Optimism had higher values than the other platform. Even so, it has shown much more ups and downs. Arbitrum has remained stable over the three months. They have similar values although Ooptimism has a slightly higher average volume bridged.  ')
st.markdown('Finally, we have analysed the user profile comparison. In Optimism, in the number of transactions by actions we see that Other is the most used option, just like in the Arbitrum platform. In the number of transactions by sector we see that in Optimism Layer2 is the most used, while in Arbitrum Dex and Layer2 are the most used.')
st.write('')

st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')
st.markdown('All the codes can be found in [Github](https://github.com/cristinatinto/The-Flippening-Comparison)')
