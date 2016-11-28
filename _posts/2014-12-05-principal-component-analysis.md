---
layout: post
title: "Principal Component Analysis: an interpretation of the covariance matrix"
date: 2014-12-05 09:00:44.000000000 +01:00
description: "Getting it right."
image: "cv-optimized.gif"
type: post
published: true
status: publish
categories: []
tags:
- machine learning
- principal component analysis
meta:
  _wpas_skip_facebook: '1'
  _wpas_skip_google_plus: '1'
  _wpas_skip_twitter: '1'
  _wpas_skip_linkedin: '1'
  _wpas_skip_tumblr: '1'
  _wpas_skip_path: '1'
  _edit_last: '4186076'
  _publicize_pending: '1'
  geo_public: '0'
author:
  login: fcmod
  email: esta.permitido@gmail.com
  display_name: Facundo Carreiro
  first_name: ''
  last_name: ''
---
A few days ago I learned about <a href="http://en.wikipedia.org/wiki/Principal_component_analysis">Principal Component Analysis</a>. In "machine learning terms", it is a method that given your set of features, synthesises a new smaller set of features which (a) represent the relevant differences in your data; and (b) they are independent of each other.

Very informally, this is done by first checking how the original features of your dataset \\(X \in \mathbb{R}^{m\times n}\\) depend on each other, by calculating the covariance matrix \\(\Sigma = X^T X / m\\) and then performing a <a href="http://en.wikipedia.org/wiki/Singular_value_decomposition">Singular Value Decomposition</a> of \\(\Sigma\\), obtaining \\(USV = \Sigma\\). The matrix \\(U \in \mathbb{R}^{n\times n}\\) gives the transformation of the original \\(n\\) features into a new set of \\(n\\) features with properties (a) and (b). However, our interest is to keep only the "most significant" of the new features so we only consider the submatrix \\(U_k := U[1\dots n,1\dots k] \in \mathbb{R}^{n\times k}\\) consisting of the first \\(k\\) columns, which represent the first \\(k\\) components. This is one of the neatest linear algebra magic tricks I've seen so far.

In order to <em>see</em> what this process was about, I decided to check the principal components of the <a href="http://fcmod.wordpress.com/2014/11/24/neural-networks-in-python/" title="Neural networks in Python">handwritten number recognition problem</a>. Recall that in this dataset, each example is a 20x20 pixel grayscale image, encoded as a 400 item vector. Therefore, a "feature" in this dataset is the intensity of a given pixel. That is why there are 400 features, one for each pixel. Again, the code was written in Python, but this time no neural networks were needed, so I basically used <code>numpy</code> (and <code>scipy</code> for plotting).

Following the process described above, I calculated the transformation matrix \\(U\\) and plotted the first 25 columns, resized to 20x20 pixel images. This picture shows the first 25 components.

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/25components.png" alt="25components" width="400" class="aligncenter wp-image-79" />
</div>

This is already beautiful. Look, the first component tell us "if you want to get the most information out of your data, you better focus on the central part of the image." This is remarkable, since everything was done automagically. The next components basically say "ok, ok, if you really need more information to tear apart your examples, then you should look at these other details over here." One could ask, what is the number of components that I should consider in order to focus on enough details of my data?

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/needed-components2.png" alt="needed-components2" width="500" class="aligncenter wp-image-87" />
</div>

Well, looks like with 100 components (or even less) you can capture most of the variance. This is remarkable! it means that, by focusing on the right points, you can go from a set of 400 features per example, to a set of 100 features per example, and (most likely) still get a good performance on whatever learning algorithm you want to use on this data. Let's see this reduction applied to a particular example.

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/error-0.png" alt="error-0" width="500" class="aligncenter wp-image-59" />
</div>

The first image is one of the examples from the dataset. The second image is that same example filtered through the first 180 components. This means that first the 400 features (pixels) of this image were converted into new 180 features, and then "projected back" into a 20x20 image.

These new features do not have a one-to-one mapping with some pixel, they represent some combination of those pixels. For example, whereas in the original image the feature \\(x_{210}\\) represents the pixel at \\((10,10)\\), the new feature \\(x'_{20}\\) may represent all the pixels of the first line at the same time, in case the algorithm realised that "usually" these pixels all have the same colour.

As you can see, the error is barely noticeable and we still get a 2x reduction on the number of features!

<strong>The covariance matrix.</strong> This method seems to work nicely, but, what is going on? I was somewhat puzzled about the covariance matrix. This \\(n\times n\\) matrix should represent, for each pair of features \\(x_i, x_j\\), how they vary together (or not). My first naive attempt to visualize it gave me the following picture.

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/covariance-wrong.png" alt="covariance-wrong" width="500" class="aligncenter wp-image-54" />
</div>

In spite of being colourful and nice, this picture doesn't give me much information. What are those gaps? And why don't I see some kind of number or zone as in the principal components?

After a while, I realised that this was a wrong representation of the phenomena in the background. This image has a dimension of 400x400 pixels, where the pixel \\((i,j)\\) represents the covariance of features \\(x_i\\) and \\(x_j\\). However, the key point is that each row (and column) represent a 20x20 pixel image, but they are flattened as a 400 pixel vector! Therefore, even though the covariance matrix is a 400x400 item matrix, it may be better seen as a 20x20x20x20 matrix. Thinking of it in a <a href="http://en.wikipedia.org/wiki/Currying">Curry-style</a> perspective, we can say that once you choose a pixel \\((x,y)\\) represented by the first two dimensions, the matrix gives you a 20x20 pixel image representing how that pixel \\((x,y)\\) relates to other of the 400 pixels.

The following are three example choices of such pixels \\((x,y)\\): one at the top-left, one in the middle section, and one close to the borders.

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/cv-examples.png" alt="cv-examples" width="400" class="aligncenter" />
</div>

<br/>
The following animation goes through other choices.

<div class="txtaligncenter">
<img src="{{ site.baseurl }}/assets/images/cv-optimized.gif" alt="cv-examples" width="700" class="aligncenter" />
</div>

Now things make more sense. My interpretation of this images is that the pixel on the top-left has a high positive correlation with the image being a number 3. This is because only the number 3 (or maybe a bit also number 7) are wide and tall enough to reach such a top-left location. The middle pixel is correlated with the central zone. Whenever this pixel has a high intensity, it is very likely that it will be surrounded by pixels with a similar intensity. The last picture shows that pixels very close to the borders are quite independent. Actually, if we look at the data, they are pretty much independently black!
