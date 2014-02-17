import sqlite3

def all_agents(c):
    """List of all agents and their info.

    Args:
        c: connection cursor to sqlite database.
    """

    sql = """SELECT ID,AgentType,ModelType,Prototype,ParentID,EnterDate,DeathDate FROM
                Agents INNER JOIN AgentDeaths ON Agents.ID = AgentDeaths.AgentID
                WHERE Agents.SimID = ? AND Agents.SimID = AgentDeaths.SimID;"""
    return c.execute(sql)

def deploy_cumulative(c):
    """Time-series of # active deployments of a specific prototype.

    Args:
        c: connection cursor to sqlite database.
    """

    sql = """SELECT ti.Time,COUNT(*)
              FROM Agents AS ag
              INNER JOIN AgentDeaths AS ad ON ag.ID = ad.AgentID
              INNER JOIN TimeList AS ti ON ti.Time >= ag.EnterDate AND ad.DeathDate > ti.Time
            WHERE
              ag.SimID = ? AND ag.SimID = ad.SimID
              AND ag.Prototype = ?
            GROUP BY ti.Time
            ORDER BY ti.Time;"""
    return c.execute(sql)

def inv_series(c):
    """Timeseries of a specific agent's inventory of a specific isotope.

    Args:
        c: connection cursor to sqlite database
    """

    sql = """SELECT ti.Time,SUM(cmp.Quantity * inv.Quantity) FROM (
                Compositions AS cmp
                INNER JOIN Inventories AS inv ON inv.StateID = cmp.ID
                INNER JOIN TimeList AS ti ON (ti.Time >= inv.StartTime AND ti.Time < inv.EndTime)
            ) WHERE (
                inv.SimID = ? AND inv.SimID = cmp.SimID
                AND inv.AgentID = ? AND cmp.IsoID = ?
            ) GROUP BY ti.Time,cmp.IsoID;"""
    return c.execute(sql)

def inv_at(c):
    """Total inventory(all isotopes) of a specific agent at specific timestep.

    Args:
        c: connection to sqlite database.
    """
    sql = """SELECT cmp.IsoID,SUM(cmp.Quantity * inv.Quantity) FROM (
                Inventories AS inv
                INNER JOIN Compositions AS cmp ON inv.StateID = cmp.ID
            ) WHERE (
                inv.SimID = ? AND inv.SimID = cmp.SimID
                AND inv.StartTime <= ? AND inv.EndTime > ?
                AND inv.AgentID = ?
            ) GROUP BY cmp.IsoID;"""
    return c.execute(sql)

def mat_created(c):
    """Total amount of material(all isotopes) created by a particular agent
    between two timesteps.

    Args:
        c: connection to a sqlite database.
    """
    sql = """SELECT cmp.IsoID,SUM(cmp.Quantity * res.Quantity) FROM (
                Resources As res
                INNER JOIN Compositions AS cmp ON res.StateID = cmp.ID
                INNER JOIN ResCreators AS cre ON res.ID = cre.ResID
            ) WHERE (
                cre.SimID = ? AND cre.SimID = res.SimID AND cre.SimID = cmp.SimID
                AND res.TimeCreated >= ? AND res.TimeCreated < ?
                AND cre.ModelID = ?
            ) GROUP BY cmp.IsoID;"""
    return c.execute(sql)

def flow(c):
    """Total material(all isotopes) transacted between two agents between two
    timesteps.

    Args:
        c: connection to sqlite database.
    """
    sql = """SELECT cmp.IsoID,SUM(cmp.Quantity * res.Quantity) FROM (
               Resources AS res
               INNER JOIN Compositions AS cmp ON cmp.ID = res.StateID
               INNER JOIN Transactions AS tr ON tr.ResourceID = res.ID
             ) WHERE (
               res.SimID = [simid] AND cmp.SimID = res.SimID AND tr.SimID = res.SimID
               AND tr.Time >= [t1] AND tr.Time < [t2]
               AND tr.SenderID = [from-agent] AND tr.ReceiverID = [to-agent]
             ) GROUP BY cmp.IsoID;"""
    return c.execute(sql)
