import numpy as np
import pandas as pd
from dowhy.causal_estimator import CausalEstimate, CausalEstimator
from sklearn.linear_model import LinearRegression
from sklearn.exceptions import NotFittedError


class DrDidAttEstimator(CausalEstimator):
    """
    Estimate the causal effect of a treatment on an outcome using the Double Robust Estimator, in
    a Differences-in-Differences (DiD) environment. It differs from
    outcome estimators such as OLS, or treatment assignment models such as Matchings, because we
    need two observations of the outcome, Y(t=0),before treatment, and Y(t=1), after treatment.
    To facilitate the analysis, the outcome in question is going to be ΔY.
    """

    def __init__(self, *args, **kwargs):
        """For a list of standard args and kwargs, see documentation for
        :class:`~dowhy.causal_estimator.CausalEstimator`.
        """
        # Required to ensure that self.method_params contains all the
        # parameters to create an object of this class
        args_dict = {k: v for k, v in locals().items() if k not in type(self)._STD_INIT_ARGS}
        args_dict.update(kwargs)
        super().__init__(*args, **args_dict)
        # Check if the treatment is one-dimensional
        if len(self._treatment_name) > 1:
            error_msg = str(self.__class__) + "cannot handle more than one treatment variable"
            raise Exception(error_msg)
        # Checking if the treatment is binary
        if not pd.api.types.is_bool_dtype(self._data[self._treatment_name[0]]):
            error_msg = "Dr-DiD method is applicable only for binary treatments"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        self.logger.debug("Back-door variables used:" + ",".join(self._target_estimand.get_backdoor_variables()))

        self._observed_common_causes_names = self._target_estimand.get_backdoor_variables()
        if self._observed_common_causes_names:
            self._observed_common_causes = self._data[self._observed_common_causes_names]

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
    
    def construct_symbolic_estimator(self, estimand):
        """
        A symbolic string that conveys what each estimator does.
        For instance, linear regression is expressed as
        y ~ bx + e
        """
        raise NotImplementedError

    def _estimate_effectfit(self):
        """A reference implementation of a fitting function.
        Parameters
        ----------
        Need X, d, delta_y
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
        X = self._observed_common_causes.to_numpy()
        d = self._treatment.to_numpy()
        delta_y = self._outcome.to_numpy()

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
        att_mean = np.mean(np.multiply(att_first_leg,att_sec_leg))        
        estimate = att_mean
        #We have to calculate att again, to calculate the variance weights
     
        att_var_weight = np.multiply(att_first_leg,att_sec_leg) - np.multiply(weight1,self.att_mean)
        self.att_var = np.mean(att_var_weight**2) 
        self.att_sd = np.sqrt(self.att_var/len(att_var_weight))
        
        return estimate
    
     
    
#def AteDrDiDEstimator(estimator,X):
#   
#    def __init__(self, X, true_control_,treatment_,alt_treatments_, delta_y):
#        self.X = X
#        self.t_ = treatment_
#        self.c_ = true_control_
#        self.at_ = alt_treatments_
#        self.y_ = delta_y
#        self.drdid = DrDidEstimator()