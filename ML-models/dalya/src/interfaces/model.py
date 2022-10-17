#standard packages
import numpy as np
import pandas as pd
import logging
import sys
#machine-learning packages
import scipy.optimize as opt
from sklearn.linear_model import LinearRegression 


from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances


class DrDidEstimator(BaseEstimator):
    
    def __init__(self):
        return
    
    def _ipt_obj_function(self,params,  *args):
        '''
        --------------------------------------------------------------------
        This function computes the Inverse Probability Tilting Estimator (IPT).
        It is the first step for the Double-Robust estimator 
        --------------------------------------------------------------------
        INPUTS as arguments:
        X_*: A matrix (n_obs x n_features) with the both treatment (D=1)
             and control (D=0) observations.
        y_*: a vector (n_obs x D), with the treatment allocation vector, ie, 
             the values will be 1/0.
        OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: 
        None
        OBJECTS CREATED WITHIN FUNCTION:
        crit_val: scalar, IPT objective function value
        FILES CREATED BY THIS FUNCTION: 
        None
        RETURNS: 
        crit_val
        --------------------------------------------------------------------
        '''
        #input list
        gamma_vec0 = params
        X_ipt_obj,y_ipt_obj = args
        #------------------------------------------------------#  
        #temp variable
        inverted_y_ipt_obj = 1 - y_ipt_obj
        #objective function value calculation
        crit_val = sum(
                       np.multiply(
                                   np.matmul(X_ipt_obj,gamma_vec0),
                                             y_ipt_obj
                                   ) -
                       np.multiply(
                                   np.exp(np.matmul(X_ipt_obj,gamma_vec0)),
                                   inverted_y_ipt_obj
                                  )
                       )       
        return -1*crit_val    

    def _wls_opt_function(self,params,  *args):
        '''
        --------------------------------------------------------------------
        This function computes the Weighted Least Squares (WLS).
        It is the second step of the DR DiD estimator
        --------------------------------------------------------------------
        INPUTS:
        X_*: The dataframe (pandas) with the control observations (D = 0). It should
                        contain the covariates in the covariates_list.
        y_*: the allocation treatment variable        
        opt_gamma_vec: The estimated IPT vector from the first step.   
        delta_outcome_var: the outcome variable at T=1 minus at T=0.
        OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        None
        OBJECTS CREATED WITHIN FUNCTION:
        crit_val: scalar, WLS objective function value
        FILES CREATED BY THIS FUNCTION: None
        RETURNS: crit_val
        --------------------------------------------------------------------
        '''
        #input list
        beta_vec0 = params
        X_wls,d_wls, opt_gamma_vec, delta_y_wls = args
        #------------------------------------------------------#
        #functions
        linear_func = np.matmul(X_wls[d_wls==0],opt_gamma_vec)
        logistic_output = np.exp(linear_func)/(1+np.exp(linear_func))
        second_leg = delta_y_wls[d_wls==0] - np.matmul(X_wls[d_wls==0],beta_vec0)
        second_leg_sq = second_leg**2
        #------------------------------------------------------#
        crit_val = sum(
                       np.multiply(logistic_output,second_leg_sq)
                       )
        return crit_val
    
    def fit(self, X, d, delta_y):
        """A reference implementation of a fitting function.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            The training input samples.
        y : array-like, shape (n_samples,) or (n_samples, n_outputs)
            The target values (class labels in classification, real numbers in
            regression).
        Returns
        -------
        self : object
            Returns self.
        """
        X, d = check_X_y(X, d, accept_sparse=True)
        self.is_fitted_ = True
        self.X_sup = np.amax(X, axis=0)
        self.X_inf = np.amin(X, axis = 0)
        # `fit` should always return `self`
        #------------------------------------------------------# 
        #0-step: the initial step vector for the IPT function is simply
        #an OLS.     
        lin_reg = LinearRegression(fit_intercept = False)
        lin_reg.fit(X, d)
        #------------------------------------------------------#
        #IPT-step
        ipt_init_params = lin_reg.coef_
        ipt_args0 = (X,d)
        print('IPT estimation started')
        opt_ipt_result = opt.minimize(self._ipt_obj_function,
                                  x0=ipt_init_params,
                                  args = ipt_args0,
                                  method = 'Nelder-Mead',
                                  options= {'disp': False})
        
        print('IPT optimation success:',opt_ipt_result.success)
        ipt_gamma_vec_hat = opt_ipt_result.x
        self.ipt_gamma_vector = ipt_gamma_vec_hat
        #------------------------------------------------------#
        #WLS-step
        lin_reg.fit(X[d==0], delta_y[d==0])
        wls_init_params = lin_reg.coef_
        wls_args0 = (X,d, ipt_gamma_vec_hat, delta_y)
        print('WLS estimation started')
        opt_wls_result = opt.minimize(self._wls_opt_function,
                                      x0=wls_init_params,
                                      args = wls_args0,
                                      method = 'Nelder-Mead',
                                      options= {'disp': False})

        print('WLS optimation success:', opt_wls_result.success)
        wls_beta_vec_hat = opt_wls_result.x
        self.wls_beta_vector = wls_beta_vec_hat
       #------------------------------------------------------#
        #weights estimator
        #W_0
        linear_func = np.matmul(X, self.ipt_gamma_vector)
        logistic_output_vec = np.exp(linear_func)/(1+np.exp(linear_func))  
        weight0_numerator = np.multiply(
                                    np.multiply(logistic_output_vec, 1-d),
                                    1/(1-logistic_output_vec)
                                    )
    
        weight0_denominator = np.mean(weight0_numerator)   
        weight0 = np.divide(weight0_numerator,weight0_denominator)
        #W_1
        d_mean = np.mean(d)
        weight1 = d/d_mean
        #-----------------------------------------------------#
        #ATT has two legs, one based on weights, other in outcomes
        att_first_leg= weight1 - weight0
        att_sec_leg= delta_y - np.matmul(X,self.wls_beta_vector)
        self.att_mean = np.mean(np.multiply(att_first_leg,att_sec_leg))        
        
        #We have to calculate att again, to calculate the variance weights
     
        att_var_weight = np.multiply(att_first_leg,att_sec_leg) - np.multiply(weight1,self.att_mean)
        self.att_var = np.mean(att_var_weight**2) 
        self.att_sd = np.sqrt(self.att_var/len(att_var_weight))
        
        return self
    
    def predict(self,X):
        check_is_fitted(self)
        
        if not ((np.all(np.amin(X,axis = 0)>=self.X_inf) and np.all(np.amax(X,axis=0)>= self.X_inf)) or (np.all(np.amax(X,axis = 0)<=self.X_sup) and np.all(np.amin(X,axis=0)<= self.X_sup))):
            logging.error('X out of support')
            sys.exit(1)
        
        result = np.repeat(self.att_mean, len(X))
        return result    
    
    
def AteDrDiDEstimator(estimator,X):
    
    def __init__(self, X, true_control_,treatment_,alt_treatments_, delta_y):
        self.X = X
        self.t_ = treatment_
        self.c_ = true_control_
        self.at_ = alt_treatments_
        self.y_ = delta_y
        self.drdid = DrDidEstimator()
    