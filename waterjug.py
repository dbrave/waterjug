#!/usr/bin/env python
'''
Created on Apr 9, 2019

@author: David Braverman
'''
from flask import Flask, request, render_template
app = Flask(__name__)
amounts_bs = []
amounts_sb = []
steps_bs = ['Both buckets are empty']
steps_sb = ['Both buckets are empty']
bucket1 = 0
bucket2 = 0
desired_amount = 0 

@app.route("/", methods=['GET'])
def hello():
    '''
    Welcome page displaying input form. Prompt user for 2 bucket capacities and
    a target measurement.
    Process input through calculate route.
    '''
    return render_template('form_page.html', message='''This application determines how to reach a desired 
                            amount of water using two buckets of specified sizes.''')

@app.route("/calculate", methods=['GET'])
def calculate_buckets():
    '''
    Take URL args, and determine shortest number of bucket operations to
    obtain the desired amount.
    http://localhost:5847/calculate?bucket1=34&bucket2=99&desired_amount=234&submit=Submit
    '''
    global bucket1
    global bucket2
    global desired_amount
    global amounts_bs
    global amounts_sb
    global steps_bs
    global steps_sb
    amounts_bs = []
    amounts_sb = []
    steps_bs = ['Both buckets are empty']
    steps_sb = ['Both buckets are empty']
    resp_data = ''
    try:
        b1 = float(request.args['bucket1'])
        b2 = float(request.args['bucket2'])
        da = float(request.args['desiredamount'])
        bucket1 = int(round(b1))
        bucket2 = int(round(b2))
        desired_amount = int(round(da))
    except ValueError:
        resp_data = ('Only numeric values are permitted.', 403)
    #response_page = 'Ok'
    print('Bucket 1 is {} gallons'.format(bucket1))
    print('Bucket 2 is {} gallons'.format(bucket2))
    print('Desired Amount is {} gallons'.format(desired_amount))
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
        steps = steps_sb
        steps.append('Fill {} gallon bucket'.format(bucket1)) 
        steps.append('Fill {} gallon bucket'.format(bucket2))
        return render_template('jug_output.html', rows=list(zip(steps, amounts)), goal=desired_amount,
                               b1name='{} Gallon Bucket'.format(bucket1), b2name='{} Gallon Bucket'.format(bucket2)), 200
        
    #If we made it this far, then we should look for the solution, otherwise...
    if resp_data != '':
        return render_template('form_page.html', message=resp_data[0]), resp_data[1]
        
    #swapped = False
    if bucket1 > bucket2:
        bucket1, bucket2 = bucket2, bucket1
        #swapped = True
    solver_bs = True
    solver_sb = True
    try:
        Solver_SB(0,0)
    except:
        print('Exception occurred (SB):')
        print(steps_sb)
        print(amounts_sb)
        solver_sb=False
    #Ignore this next line. It's not like I wrote the routine backwards or anything...     
    bucket1, bucket2 = bucket2, bucket1
    try:
        Solver_BS(0,0)
    except:
        print('Exception occurred (BS):')
        print(steps_bs)
        print(amounts_bs)
        solver_bs = False 
    print(steps_sb)
    print(steps_bs) 
    if len(steps_bs) < len(steps_sb) and solver_bs == True:
        return render_template('jug_output.html', rows=list(zip(steps_bs, amounts_bs)), goal=desired_amount, 
                               b1name='{} Gallon Bucket'.format(bucket1), b2name='{} Gallon Bucket'.format(bucket2)), 200
        
    elif solver_sb == True:
        return render_template('jug_output.html', rows=list(zip(steps_sb, amounts_sb)), goal=desired_amount,
                               b1name='{} Gallon Bucket'.format(bucket1), b2name='{} Gallon Bucket'.format(bucket2)), 200
    else:
        return render_template('form_page.html', message='An error occurred. Please check the applicaton log.'), 200    

def GCD(a, b):
    '''
    Return the Greatest Common Divisor for two numbers.
    '''  
    if a == 0: 
        return b  
      
    return GCD(b % a, a) 

def Solver_SB(bucket1_contents, bucket2_contents):
    '''
    Solve by going from the smaller bucket to the larger bucket.
    '''
    amounts_sb.append((bucket1_contents, bucket2_contents))
    if bucket2_contents == desired_amount or bucket1_contents + bucket2_contents == desired_amount:
        steps_sb.append('Done!')
        return
    elif bucket2_contents == bucket2:
        steps_sb.append('Empty {} gallon bucket and transfer {} gallon bucket content to it.'.format(bucket2, bucket1))
        if bucket1_contents == 0:
            print(steps_sb)
            print(amounts_sb)
            raise StandardError('Solution not possible')
        Solver_SB(0, bucket1_contents)
    elif bucket1_contents != 0 and bucket2_contents == 0:
        steps_sb.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_SB(0, bucket1_contents)
    elif bucket1_contents == desired_amount:
        steps_sb.append('Empty {} gallon bucket'.format(bucket2))
        Solver_SB(bucket1_contents, 0)
    elif bucket1_contents < bucket1:
        steps_sb.append('Fill {} gallon bucket'.format(bucket1))
        Solver_SB(bucket1, bucket2_contents)
    elif bucket1_contents < (bucket2-bucket2_contents):
        steps_sb.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_SB(0, (bucket1_contents+bucket2_contents))
    else:
        steps_sb.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_SB(bucket1_contents-(bucket2-bucket2_contents), (bucket2-bucket2_contents)+bucket2_contents)

def Solver_BS(bucket1_contents, bucket2_contents):
    '''
    Solve by going from the larger bucket to the smaller bucket.
    '''
    amounts_bs.append((bucket1_contents, bucket2_contents))
    if bucket2_contents == desired_amount or bucket1_contents + bucket2_contents == desired_amount:
        steps_bs.append('Done!')
        return
    elif bucket2_contents == bucket2:
        steps_bs.append('Empty {} gallon bucket'.format(bucket2))
        if bucket1_contents is 0:
            raise StandardError('Solution not possible')
        Solver_BS(bucket1_contents, 0)         
    elif bucket1_contents != 0 and bucket1_contents < (bucket2-bucket2_contents):
        steps_bs.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_BS(0, (bucket1_contents+bucket2_contents))

    elif bucket1_contents != 0 and bucket2_contents == 0:
        steps_bs.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_BS(bucket1_contents-(bucket2-bucket2_contents), (bucket2-bucket2_contents)+bucket2_contents)
    elif bucket1_contents == desired_amount:
        steps_bs.append('Empty {} gallon bucket'.format(bucket2))
        Solver_BS(bucket1_contents, 0)
    elif bucket1_contents < bucket1:
        steps_bs.append('Fill {} gallon bucket'.format(bucket1))
        Solver_BS(bucket1, bucket2_contents)
    else:
        steps_bs.append('Transfer {} gallon bucket content to {} gallon bucket'.format(bucket1, bucket2))
        Solver_BS(bucket1_contents-(bucket2-bucket2_contents), (bucket2-bucket2_contents)+bucket2_contents)


if __name__ == '__main__':
    print('Running on port JUGS (5847)')
    app.run(host='0.0.0.0', port=5847, debug=True, threaded=True)