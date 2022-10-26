#standard packages
import numpy as np
import pandas as pd
import logging
import sys
#machine-learning packages





class StaggDiD:
    """
    A motherfuckery Diff-in-Diff class, that uses Callaway and Santana's 2021 method to estimate the effect of a treatment on a population.
    
    Methods
    -------
    att() -> np.ndarray(3)
        estimate the average treatment effect on the treated, based on the data provided, as well as confidence intervals.
    
    Attributes
    ----------
    a: str
        The data warehouse to connect to. Only PostgreSQL or Redshift is supported.
    b: str
        The port to connect to the data warehouse.
    c: str
        The region where the data warehouse is located.
    d: str
        The name of the database to connect to.
    """

    def __init__() -> None:
        pass
    
    def att(df: pd.DataFrame, member_id:str, treatment: str, outcome: str, time: str, start_time:int, end_time:int):
        """
        A method that calculates the att and confidence intervals
        treatment: a string representing the name of the column of the treatment variable, dummy variable 1/0.
        outcome:a string representing the name of of the outcome variable, continuous/dummy/multi-valued.
        time: a string representing the name of time variable, with 0 being the start time of the treatment, -3,-2,-1...pre-treatment period, 1,2,3... post-treatment period.
        start_time: The start time of analysis. Must be negative to represent a pre-treatment period
        end_time: The end time of analysis. Must be positive to represent a post-treatment period.
        -------
        Attributes
        ----------
        mean: np.array()
        the mean of outcome in treatment minus the mean of outcome in control
        lower_bound: np.array()
        the lower bound of the confidence interval
        upper_bound: np.array()
        the upper bound of the confidence interval
        """

        #Create empty DataFrame with specific column names & types
        att_df = pd.DataFrame({'time': pd.Series(dtype='int'),
                        'lower_bound': pd.Series(dtype='float'),
                        'mean': pd.Series(dtype='float'),
                        'upper_bound': pd.Series(dtype='float')})
        if start_time <0:
            time_interval = [x for x in range(start_time, end_time+1) if x in (df[df[treatment]==1][time].unique())]
            
            att_df['time'] = time_interval;

            for t in  att_df['time']:
                temp_treat_df = df[(df[time] == t) & (df[treatment] == 1)][[member_id,outcome]].merge(df[(df[time] == -1) & (df[treatment] == 1)][[member_id,outcome]], how = 'inner', on = member_id);
                mean_treat = np.mean(np.subtract(temp_treat_df[outcome + '_x'],temp_treat_df[outcome + '_y']));
                var_treat = np.var(np.subtract(temp_treat_df[outcome + '_x'],temp_treat_df[outcome + '_y']))/len(temp_treat_df);
                temp_ctrl_df = df[(df[time] == t) & (df[treatment] == 0)][[member_id,outcome]].merge(df[(df[time] == -1) & (df[treatment] == 0)][[member_id,outcome]], how = 'inner', on = member_id);
                mean_ctrl = np.mean(np.subtract(temp_ctrl_df[outcome + '_x'],temp_ctrl_df[outcome + '_y']));
                var_ctrl = np.var(np.subtract(temp_ctrl_df[outcome + '_x'],temp_ctrl_df[outcome + '_y']))/len(temp_ctrl_df);
                temp_att_dist = [(mean_treat - mean_ctrl), (var_treat + var_ctrl)];
                att_df.loc[(att_df['time'] == t), 'lower_bound'] = temp_att_dist[0] - 1.96*np.sqrt(temp_att_dist[1])
                att_df.loc[(att_df['time'] == t), 'mean'] = temp_att_dist[0]
                att_df.loc[(att_df['time'] == t), 'upper_bound'] = temp_att_dist[0] + 1.96*np.sqrt(temp_att_dist[1])

        if start_time >=0:
            time_interval = [x for x in range(start_time, end_time+1) if x in df[df[treatment]==1][time].unique()]
    
            att_df['time'] = time_interval;

            for t in  att_df['time']:
                temp_treat_df = df[(df[time] == t) & (df[treatment] == 1)][[member_id,outcome]].merge(df[(df[time] == 0) & (df[treatment] == 1)][[member_id,outcome]], how = 'inner', on = member_id);
                mean_treat = np.mean(np.subtract(temp_treat_df[outcome + '_x'],temp_treat_df[outcome + '_y']));
                var_treat = np.var(np.subtract(temp_treat_df[outcome + '_x'],temp_treat_df[outcome + '_y']))/len(temp_treat_df);
                temp_ctrl_df = df[(df[time] == t) & (df[treatment] == 0)][[member_id,outcome]].merge(df[(df[time] == 0) & (df[treatment] == 0)][[member_id,outcome]], how = 'inner', on = member_id);
                mean_ctrl = np.mean(np.subtract(temp_ctrl_df[outcome + '_x'],temp_ctrl_df[outcome + '_y']));
                var_ctrl = np.var(np.subtract(temp_ctrl_df[outcome + '_x'],temp_ctrl_df[outcome + '_y']))/len(temp_ctrl_df);
                temp_att_dist = [(mean_treat - mean_ctrl), (var_treat + var_ctrl)];
                att_df.loc[(att_df['time'] == t), 'lower_bound'] = temp_att_dist[0] - 1.96*np.sqrt(temp_att_dist[1])
                att_df.loc[(att_df['time'] == t), 'mean'] = temp_att_dist[0]
                att_df.loc[(att_df['time'] == t), 'upper_bound'] = temp_att_dist[0] + 1.96*np.sqrt(temp_att_dist[1])

        return att_df
