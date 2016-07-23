---
layout: post
title: Neural networks in Python
date: 2014-11-24 10:08:51.000000000 +01:00
type: post
description: "Neurolab, Octave and error functions."
image: "numbers.png"
published: true
status: publish
categories: []
tags:
- machine learning
- neural networks
- neurolab
meta:
  _wpas_skip_facebook: '1'
  _wpas_skip_google_plus: '1'
  _wpas_skip_twitter: '1'
  _wpas_skip_linkedin: '1'
  _wpas_skip_tumblr: '1'
  _wpas_skip_path: '1'
  _publicize_pending: '1'
  _rest_api_published: '1'
  _rest_api_client_id: "-1"
  _edit_last: '4186076'
  geo_public: '0'
author:
  login: fcmod
  email: esta.permitido@gmail.com
  display_name: fcmod
  first_name: ''
  last_name: ''
---
I'm about to finish the course on Machine Learning from Stanford University (via Coursera). I have really enjoyed it and I super recommend it. Andrew is an awesome teacher and the contents cover quite some topics. During the course I used Octave and Matlab to code, and now that the course is coming to an end I thought it was time to try to do some machine learning with other tools.

As I like Python, I started to look for machine learning and visualisation frameworks. After some time trying out stuff (on OSX) I found <a href="http://continuum.io/downloads" target="_blank">Anaconda</a> which seems to integrate many of the basic frameworks I was looking for (scipy, numpy, ipython). They provide precompiled binaries for OSX (64 bits), which is extremely handy. However, Anaconda does not include any neural networks framework.

As a first test I wanted to create a small neural network and play with it. One of the first packages that I found was <a href="https://code.google.com/p/neurolab/">neurolab</a>. After using it a bit, I'm somewhat doubtful about its quality and flexibility, but we'll get to that later. My first task was to use the date provided in the course to train a small neural network to do multi-class classification of handwritten digits (as in the course, but this time in Python).

<div class="txtaligncenter">
<img class="wp-image-7 aligncenter" style="border:0 solid #000000;" src="{{ site.baseurl }}/assets/images/numbers.png" alt="handwritten symbols" width="400" height="400" />
</div>

The training set consists of 5000 images of 20x20 pixels tagged with a number from 1 to 10. During the course I implemented back-propagation on a 400x25x10 neural network. The training (minimisation) process is done using a function called <code>fmincg</code> which I assume implements the "<a href="http://en.wikipedia.org/wiki/Conjugate_gradient_method" target="_blank">conjugate gradient</a>" method. After 100 iteration the cost function goes from 3.0 to 0.3 and the network shows the following accuracy on the training set:

<pre>Training Set Accuracy (Octave): 98.200000</pre>

On the Python side things turn out to be quite different: thanks to numpy, it was pretty easy to load the input data, even though it was saved in matlab's format. So far so good. When I run the training algorithm with a limit of 400 epochs the process hangs in the second epoch. That's bad. After looking around a bit I realise that the trainer was using the <a href="http://en.wikipedia.org/wiki/Broyden%E2%80%93Fletcher%E2%80%93Goldfarb%E2%80%93Shanno_algorithm">BFGS algorithm</a> for training.
<pre>BroydenFletcherGoldfarbShanno (BFGS) method
Using scipy.optimize.fmin_bfgs</pre>
I set it up to use conjugate gradient and ran it again. Now things move, a lot faster actually. To my surprise, however, the error seems to be going down slowly and is in the order of the <em>thousands</em>!
<pre>16532.013986138914
12211.253063515749
9321.548001261297
7447.4908200988111
6117.6342796750459
5154.1937944235206
4059.7467562874954
3377.849932612688
2886.6254179185016
2689.2482473483706
...</pre>
This is strange, given that in Octave I was getting error lesser than 3.0, with something that I implemented myself and therefore expect to be worse than <code>scipy</code>. In any case, I thought, maybe the errors are just calculated differently. In Octave, I defined the cost function to be a generalisation of the cost function for logistic regression with regularisation, that is:

$$
J(\theta) = - \frac{1}{m} \left[ \sum_{i=1}^m y^{(i)}\ log (h_\theta (x^{(i)})) + (1 - y^{(i)})\ log (1 - h_\theta(x^{(i)}))\right] + \frac{\lambda}{2m}\sum_{j=1}^n \theta_j^2
$$

When I check which error function was being used by neurolab I see that it is the <strong>Sum of Squared Errors</strong>. Hmm... I wonder if "error function" and "cost function" are not being used as synonyms. In that case, maybe the trainer minimises the correct "cost" function but reports the error using an "error" function. Well, apparently not: the optimisation call is

```python
fmin_bfgs(self.fcn, self.x.copy(), fprime=self.grad,
          callback=self.step,**self.kwargs)
```

and <code>self.fcn</code> is defined as

```python
def fcn(self, x):
    self.x[:] = x
    err = self.error(self.net, self.input,
                     self.target)
    self.lerr = err
    return err
```

So it seems that the error function (in this case SSE) is the one being minimized. Maybe I could write a new error function myself, lets see how they are defined:

```python
class SSE:
    """
    Sum squared error function

    :Parameters:
        e: ndarray
            current errors: target - output
    :Returns:
        v: float
            Error value
    """

    def __call__(self, e):
        v = 0.5 * np.sum(np.square(e))
        return v

    def deriv(self, e):
        """
        Derivative of SSE error function

        :Parameters:
            e: ndarray
                current errors: target - output
        :Returns:
            d: ndarray
                Derivative: dE/d_out
        """
        return e
```

The input is <code>target - ouput</code> so there is no possible way to calculate the \\(J(\theta)\\) function I need, as I don't have access to \\(\theta\\) or \\(h_\theta(x)\\). Let alone that the derivative is not even calculated here. Well, as there doesn't seem to be a straightforward way to change the error function, let's see how the training process compares.

By then, on the Python side I had already performed ~20.000 epochs on my network using the conjugate gradient method and the SSE error function. When I check the accuracy on the training set I get:
<pre>Training Set Accuracy (cd+sse, 20000 epochs): 98.790000</pre>
Okay, it's good, even slightly higher than the one I got in Octave. But this is not fair, there I only ran the training for 100 epochs, so let's see how this network performs with only 100 epochs.
<pre>Training Set Accuracy (cd+sse, 100 epochs): 80.700000</pre>
It performs a lot worse.

<strong>Conclusion.</strong> I think that the default setup of <code>neurolab</code> with the SSE error metric is probably better suited for solving <em>regression</em> problems. However, in this case, I was trying to solve a (multi-class) <em>classification</em> problem. Even though it was not explained in the course I now assume that the log-based cost function is better suited for this kind of problems. I still need to do further research (reading) to see if this is the case. On the technical side, I don't quite like the architecture of <code>neurolab</code> and the fact that you cannot easily implement other broader cost functions. I think I'll try other library and see how they compare.

<strong>Update.</strong> I found the following <a href="http://stackoverflow.com/questions/12157881/cost-function-for-logistic-regression">intuitive explanation</a> to this problem in StackOverflow, by user <a href="http://stackoverflow.com/users/166749/larsmans">larsman</a>:

> The squared-error loss from linear regression isn't used because it doesn't approximate zero-one-loss well: when your model predicts +50 for some sample while the intended answer was +1 (positive class), the prediction is on the correct side of the decision boundary so the zero-one-loss is zero, but the squared-error loss is still 49² = 2401. Some training algorithms will waste a lot of time getting predictions very close to {-1, +1} instead of focusing on getting just the sign/class label right.

Nice to know!
