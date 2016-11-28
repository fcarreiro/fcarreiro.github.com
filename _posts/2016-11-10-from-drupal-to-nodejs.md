---
layout: post
title: From Drupal to NodeJS without breaking mobile compatibility
date: 2016-11-10
type: post
description: "Deploying a backwards-incompatible API without breaking the mobile apps."
image: "legacy-fire.png"
published: true
status: publish
categories: []
tags:
- nodejs
- backend
- web development
author:
  login: fcmod
  email: esta.permitido@gmail.com
  display_name: fcmod
  first_name: ''
  last_name: ''
---
One of my latest clients hired me to work on a project which consisted of

 * A web frontend (mostly AngularJS)
 * Mobile applications (iOS and Android using Titanium)
 * A backend (written in Drupal)

The problem was that their traffic had suddenly increased and Drupal couldn't take it anymore. Their average response time was **14 seconds**, and each process was using **1.2GB** of memory.

<div class="txtaligncenter"><br/>
<img src="/assets/images/legacy-fire.png" width="650" class="aligncenter" />

<img src="/assets/images/mem-drupal.png" width="650" class="aligncenter" /><br/>
<span class="figure">Fig 1: Drupal (PHP) response time and memory usage. I love New Relic!</span>
</div>
<br>

One of my tasks was to rewrite the backend using `NodeJS`. So far so good. I like bringing order to chaos, and this would give me the chance to write a new, elegant and performant backend while at the same time redesigning the database schema and whatever I needed. That was an important point, since Drupal uses an extremely complex database schema to account for generality and extensibility. In this case, we didn't need that, we needed a fast and maintainable API.

Right from the beginning we knew that the new API was going to be **backwards-incompatible**, since the current API returned, in some cases, Drupal objects and not general structures. Moreover, the current API's interface was overly-complicated, partly because of limitations in Drupal, and partly because it had been growing with patches over patches.

At first sight, the steps to take may seem simple: I should design the new API interface in conjunction with mobile and frontend developers. They mock the API calls and prepare the new versions. We send the new back- and front-ends to staging. We publish to production. Happiness.

Not quite so... there is a small problem with the mobile applications. No matter how you send your apps to the app store, there will be a point in time when both the old and versions are being used. These two versions will expect different interfaces. And we wanted both the old and new mobile apps to work correctly at the same time. Which possible solutions come to mind?

(1) **Force the user to update the mobile apps when the new version is available**: this could have worked, but in our scenario we were dealing with both Android and iOS app stores, and you cannot easily synchronize the availability of the app in both stores. This creates a problem since there wouldn't be a clear moment to migrate to the new API without losing service.

(2) **Run both the Drupal and NodeJS backends for a while**: this was the solution suggested to me by the team. Let me explain why this solution is extremely painful (and not time-effective). First I'll focus on the database. If we were to have both backends coexisting then we either (a) write the new API using the bloated Drupal DB schema, or (b) use a new schema but keep the new and old tables synchronized. Both options are terrible, they involve a lot of extra development time just for the transition. Even if we don't consider the DB, running both backends side-by-side was not really going to work, since the servers were already on fire running Drupal alone.

(3) **Focus on routes, and adapt the data**: the solution I came up with was based on the fact that it didn't matter whether Drupal was running or not, as long as the mobile applications thought it was. Strictly speaking this only means that the routes they try to access have to respond, and that they have to respond in the format that the mobile apps expect. My suggestion was to implement an *adaptor* for this purpose, a thin compatibility layer.

## The solution

For the final solution I focused on the new API. I designed it from the ground up, using straightforward code and a database schema which actually represented the domain. Once that was done, I set it up at `api.example.com`. We tried the NodeJS API with the new mobile apps and everything was working correctly.

The old API (drupal) was responding at `legacy.example.com`. First I configured `nginx` to redirect those calls to `api.example.com/legacy`. Next, I set up new route handlers for the old interface which, when needed, translated the input format to conform with the new API. After executing one or more calls to the new API, the adaptor would massage the resulting structure to conform with what the old mobile applications were expecting.

```
legacy call -> adapt input -> call nodejs API -> adapt output
```

This layer was really thin and quick to code, and it had many nice properties. To name a few: (1) Drupal and PHP did not need to run; (2) the concerns were separated! The NodeJS API code was definitive, there was no need to modify it after the transition, only drop the compatibility routes; (3) no synchronization was needed; (4) there was no need to mimic Drupal's behaviour on its own database schema.

## Performance and memory consumption

The new API ended up performing consistently better than the Drupal API. This is no surprise, since Drupal was not designed to be used as it was being used here.

The average response time went down to **330ms** and each NodeJS process was using around **100MB** of memory.

<div class="txtaligncenter"><br>
<img src="/assets/images/time-node.png" width="650" class="aligncenter" />
</div>
<br>

As you can see in the graph, most of the time was actually spent in by the `MySQL` process. That is, in database calls. This makes it clear that the system could most likely benefit from *caching*. However, as the storm had passed and the servers (and service) were functioning again, my client preferred to postpone those tasks for the future ;)
