---
date: 2026-03-18
title: "It never is just a button: concerns when running code in someone else's computer"
authors:
    - dodge
categories:
    - Tech
tags:
    - anonymity
    - fingerprinting
    - privacy
---

> — "There was a button", Holden said. "I pushed it."  
> — Jesus Christ. That really is how you go through life, isn't it?

## Introduction

Ever since JavaScript was introduced, we have had concerns with security issues leading to the current patchwork
of rules, headers and sandbox that browsers have had to implement reactively. After billions of dollars invested,
we have billions of devices running the best sandbox ever which is Chromium's V8. But is that enough?

<!-- more -->

## POC

Have you heard of [bookmarklets](https://en.wikipedia.org/wiki/Bookmarklet)? If not, even better, I'd say. No need to
even look it up because, well, this is a demo post and I'll guide you through it. Honestly I'd even appreciate it
if you don't look it up just yet.
