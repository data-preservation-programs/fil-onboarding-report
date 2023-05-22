import os

import pandas as pd
import psycopg2
import streamlit as st


# Helper functions
def int_client_id(client):
    if client.startswith("f"):
        return client[1:].strip()
    return client.strip()


def client_id_query(client_ids):
    return " OR ".join(["client_id = '{client_id}'".format(client_id=int_client_id(i)) for i in client_ids])


# Database queries
def top_clients_for_last_week(first_day, last_day, top_n=10):
    return load_oracle(
        """
            SELECT client_id, SUM((1::BIGINT << claimed_log2_size) / 1024 / 1024 / 1024) AS size
            FROM published_deals
            WHERE (status = 'active' OR status = 'published')
            AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
            GROUP BY client_id
            ORDER BY size DESC
            LIMIT '{top_n}';
        """.format(fday=first_day, lday=last_day, top_n=top_n)
    ).rename(columns={"client_id": "Client ID", "size": "Onchain"})


def active_or_published_daily_size(first_day, last_day, client_ids):
    df = load_oracle(
        """
            SELECT sq.client_id as client_id, DATE_TRUNC('day', sq.ts_from_epoch) AS dy, SUM((1::BIGINT << sq.claimed_log2_size) / 1024 / 1024 / 1024) AS size, COUNT(sq.claimed_log2_size) AS pieces
            FROM (
                SELECT client_id, piece_id, ts_from_epoch(sector_start_rounded), claimed_log2_size
                FROM published_deals
                WHERE 
        """
        + client_id_query(client_ids)
        +
        """
                AND (status = 'active' OR status = 'published')
                AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
                ORDER BY piece_id, entry_created
            ) sq
            GROUP BY sq.client_id, DATE_TRUNC('day', sq.ts_from_epoch);
        """.format(fday=first_day, lday=last_day, client_id=client_ids[0])
    ).rename(columns={"dy": "PTime", "size": "Onchain", "pieces": "Pieces"})

    df["Day"] = pd.to_datetime(df.PTime).dt.tz_localize(None)
    df["client_id"] = "f" + df["client_id"].astype(str)
    return df


def copies_count_size(first_day, last_day, client_ids):
    return load_oracle(
        """
            SELECT sq.copies, COUNT(sq.copies), SUM((1::BIGINT << sq.sz) / 1024 / 1024 / 1024) AS size
            FROM (
                SELECT COUNT(piece_id) AS copies, MAX(claimed_log2_size) AS sz
                FROM published_deals
                WHERE
        """
        + client_id_query(client_ids)
        +
        """
                AND (status = 'active' OR status = 'published')
                AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
                GROUP BY piece_id
            ) sq
            GROUP BY copies;
        """.format(fday=first_day, lday=last_day)
    ).rename(columns={"copies": "Copies", "count": "Count", "size": "Size"})


def provider_item_counts(first_day, last_day, client_ids):
    return load_oracle(
        """
            SELECT provider_id, count(1) AS cnt
            FROM published_deals
            WHERE
        """
        + client_id_query(client_ids)
        +
        """
            AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
            GROUP BY provider_id
            ORDER BY cnt DESC;
        """.format(fday=first_day, lday=last_day)
    ).rename(columns={"provider_id": "Provider", "cnt": "Count"})


def deal_count_by_status(first_day, last_day, client_ids):
    return load_oracle(
        """
            SELECT status, count(1)
            FROM published_deals
            WHERE
        """
        + client_id_query(client_ids)
        +
        """
            AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
            GROUP BY status;
        """.format(fday=first_day, lday=last_day)
    ).rename(columns={"status": "Status", "count": "Count"})


def terminated_deal_count_by_reason(first_day, last_day, client_ids):
    return load_oracle(
        """
            SELECT published_deal_meta->>'termination_reason' AS reason, count(1)
            FROM published_deals
            WHERE
        """
        + client_id_query(client_ids)
        +
        """
            AND status = 'terminated'
            AND ts_from_epoch(sector_start_rounded) BETWEEN '{fday}' AND '{lday}'
            GROUP BY reason;
        """.format(fday=first_day, lday=last_day)
    ).rename(columns={"reason": "Reason", "count": "Count"}) \
        .replace("deal no longer part of market-actor state", "expired") \
        .replace("entered on-chain final-slashed state", "slashed")


def index_age():
    return load_oracle(
        """
            SELECT ts_from_epoch( ( metadata->'market_state'->'epoch' )::INTEGER )
            FROM global;
        """
    )


@st.cache_data(ttl=3600, show_spinner="Loading Oracle Results...")
def load_oracle(dbq):
    DBSP = "SET SEARCH_PATH = naive;"
    with psycopg2.connect(database=os.getenv("DBNAME"), host=os.getenv("DBHOST"), user=os.getenv("DBUSER"),
                          password=os.getenv("DBPASS"), port=os.getenv("DBPORT")) as conn:
        conn.cursor().execute(DBSP)
        return pd.read_sql_query(dbq, conn)
