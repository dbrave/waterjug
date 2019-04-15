#!/usr/bin/env python
'''
Created on Apr 9, 2019

@author: David Braverman
'''
from flask import Flask, request, render_template, send_from_directory
import sys
app = Flask(__name__, static_folder='static')

@app.route("/", methods=['GET'])
def startup():
    '''
    Welcome page displaying input form. Prompt user for 
    2 bucket capacities and a target measurement.
    Process input through calculate route.
    '''
    return render_template('form_page.html', message='''This application determines how to reach a desired 
                            amount of water using two buckets of specified sizes.''')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def log(output):
    '''
    print debug statements to stderr
    '''
    print(output, file=sys.stderr)

@app.route("/calculate", methods=['GET'])
def calculate():
    '''
    Take URL args, and determine shortest number of bucket operations to
    obtain the desired amount.
    http://localhost:5847/calculate?bucket1=34&bucket2=99&desired_amount=234&submit=Submit
    '''
    resp_data = ''
    # Sanitize input
    try:
        b1 = float(request.args['bucket1'])
        b2 = float(request.args['bucket2'])
        da = float(request.args['desiredamount'])
        bucket1 = int(round(b1))
        bucket2 = int(round(b2))
        desired_amount = int(round(da))
    except ValueError:
        resp_data = ('Only numeric values are permitted.', 403)
        return render_template('form_page.html', message=resp_data[0]), resp_data[1]
    #response_page = 'Ok'
    log('Bucket 1 is {} gallons'.format(bucket1))
    log('Bucket 2 is {} gallons'.format(bucket2))
    log('Desired Amount is {} gallons'.format(desired_amount))
    # Check for some obvious stuff
    if bucket1 + bucket2 < desired_amount:
        resp_data = ('No Solution. You need bigger buckets to achieve desired amount.', 418)
    if desired_amount % GCD(bucket1, bucket2) != 0:
        resp_data = ('No Solution. No way to achieve desired amount with specified buckets', 418)
    if bucket1 < 1:
        resp_data = ('Bucket 1 must be greater than 0', 200)
    if bucket2 < 1:
        resp_data = ('Bucket 2 must be greater than 0', 200)
    if bucket1 + bucket2 == desired_amount:
        amounts = [(0,0), (bucket1, 0), (bucket1, bucket2)]
        steps = ['Both buckets are empty']
        steps.append('Fill {} gallon bucket'.format(bucket1)) 
        steps.append('Fill {} gallon bucket'.format(bucket2))
        return render_template('jug_output.html', rows=list(zip(steps, amounts)), goal=desired_amount,
                               b1name='{} Gallon Bucket'.format(bucket1), b2name='{} Gallon Bucket'.format(bucket2)), 200
        
    #If there was an issue, tell the user and start over.
    if resp_data != '':
        return render_template('form_page.html', message=resp_data[0]), resp_data[1]
        
    jug = WaterJug(bucket1, bucket2, desired_amount)
    steps, amounts = jug.Solve()
    if steps is not None:
        return render_template('jug_output.html', rows=list(zip(steps, amounts)), goal=desired_amount, 
                                b1name='{} Gal. Bucket'.format(bucket1), b2name='{} Gal. Bucket'.format(bucket2)), 200
    else:
        return render_template('form_page.html', message='''An error occurred. Please check the application log.''')        
def GCD(a, b):
    '''
    Return the Greatest Common Divisor for two numbers. If the desired_amount 
    is not a multiple of the GCD, then there is no solution.
    '''  
    if a == 0: 
        return b  
      
    return GCD(b % a, a) 


class WaterJug(object):
    '''
    Calculate water jug problem in two ways: Going from small to large, and large to small. 
    Return the shortest solution. 
    '''
    def __init__(self, bucket1, bucket2, goal):
        if bucket1 > bucket2:
            bucket1, bucket2 = bucket2, bucket1
        self.bucket1 = bucket1
        self.bucket2 = bucket2
        self.goal = goal
        self.amounts = []
        self.steps = ['Both buckets are empty']
        
    def Solve(self):
        '''
        Wrapper
        '''
        solver_bs = True
        solver_sb = True
        try:
            #self.Solver_SB(0,0)
            self.Solver(0,0)
        except:
            log('Exception occurred (SB):')
            log(self.steps)
            log(self.amounts)
            solver_sb=False
        #Ignore this next line. It's not like I wrote the routine backwards or anything...     
        self.steps_sb=self.steps.copy()
        self.amounts_sb=self.amounts.copy()
        self.amounts = []
        self.steps = ['Both buckets are empty']
        #Swap buckets
        self.bucket1, self.bucket2 = self.bucket2, self.bucket1
        try:
            self.Solver(0,0)
        except:
            log('Exception occurred (BS):')
            log(self.steps)
            log(self.amounts)
            solver_bs = False
        self.steps_bs=self.steps
        self.amounts_bs=self.amounts
             
        #Some debug output for demonstration purposes
        log('Small to Large is {} steps.'.format(len(self.steps_sb)))
        log('Large to Small is {} steps.'.format(len(self.steps_bs))) 
        if len(self.steps_bs) < len(self.steps_sb) and solver_bs == True:
            return self.steps_bs, self.amounts_bs
        elif solver_sb == True:
            return self.steps_sb, self.amounts_sb
        else:
            return None, None
           
    def Solver(self, bucket1_contents, bucket2_contents):
        '''
        Recursive function to either go from small bucket to large, or vice versa.
        '''
        self.amounts.append((bucket1_contents, bucket2_contents))
        if bucket2_contents == self.goal or bucket1_contents + bucket2_contents == self.goal:
            return
        elif bucket2_contents == self.bucket2:
            self.steps.append('Empty {} gallon bucket'.format(self.bucket2))
            if bucket1_contents == 0:
                raise StandardError('Solution not possible')
            self.Solver(bucket1_contents, 0)         
        elif bucket1_contents != 0 and bucket1_contents < (self.bucket2-bucket2_contents):
            self.steps.append('Transfer {} gallon bucket content to {} gallon bucket'.format(self.bucket1, self.bucket2))
            self.Solver(0, (bucket1_contents+bucket2_contents))   
        elif bucket1_contents != 0 and bucket2_contents == 0:
            self.steps.append('Transfer {} gallon bucket content to {} gallon bucket'.format(self.bucket1, self.bucket2))
            self.Solver(bucket1_contents-(self.bucket2-bucket2_contents), (self.bucket2-bucket2_contents)+bucket2_contents)
        elif bucket1_contents == self.goal:
            self.steps.append('Empty {} gallon bucket'.format(self.bucket2))
            self.Solver(self.bucket1_contents, 0)
        elif bucket1_contents < self.bucket1:
            self.steps.append('Fill {} gallon bucket'.format(self.bucket1))
            self.Solver(self.bucket1, bucket2_contents)
        else:
            self.steps.append('Transfer {} gallon bucket content to {} gallon bucket'.format(self.bucket1, self.bucket2))
            self.Solver(bucket1_contents-(self.bucket2-bucket2_contents), (self.bucket2-bucket2_contents)+bucket2_contents)


if __name__ == '__main__':
    log('Running on port JUGS (5847)')
    app.run(host='0.0.0.0', port=5847, debug=True, threaded=True)