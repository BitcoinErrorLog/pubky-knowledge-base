---
title: "Mike Hearn correspondence thread 2"
author: "Mike Hearn and Satoshi Nakamoto"
date: "Sat, Apr 25, 2009 at 9:30 PM"
original_url: "https://plan99.net/~mike/satoshi-emails/thread2.html"
archive_url: "https://plan99.net/~mike/satoshi-emails/thread2.html"
source_collection: "mike-hearn-correspondence"
rights_status: "recipient-published correspondence; source text retained at operator direction"
retrieval_date: "2026-09-28"
checksum: "sha256:0dc6d0858c9a3a0c638039e1811be879aa568b64b93388357d0710d91c5e4117"
---

Lack of chargeback support
4 messages

Mike Hearn <mike@plan99.net>Sat, Apr 25, 2009 at 9:30 PMTo: Satoshi Nakamoto <satoshin@gmx.com>
Hi Satoshi,

I just read the following wiki page:

http://en.wikipedia.org/wiki/Chargeback

which claims that "U.S. debit card holders are guaranteed reversal

rights by Federal Reserve Regulation E under the Electronic Funds

Transfer Act. Similar rights extend globally pursuant to the rules

established by the corresponding card association or bank network."

The "Electronic Funds Transfer Act" sounds awfully generic, do you

think it'd apply to BitCoin? If so, would the inability to do

chargebacks risk making it illegal?

Satoshi Nakamoto <satoshin@gmx.com>Mon, Apr 27, 2009 at 12:11 AMTo: Mike Hearn <mike@plan99.net>
I am not a lawyer and I can't possibly answer that.  I suppose if the law applies to a bank or financial institution or other intermediary, then it would not apply since there is no bank involved, only two parties trading directly with each other, as they would in person with cash or barter with physical commodities.

Bitcoin is fundamentally designed to be able to do non-reversible transactions, and there certainly are applications that need that.

If someone wants the possibility of chargeback, they can use an escrow transaction, which isn't implemented yet but will be one of the next things.  For instance, a transaction can be written to designate a third party to decide whether it is returned if the payer does not release it, with auto-release after a number of days.  I'll implement a more basic form of escrow first, but the network infrastructure includes a predicate language that can express any number of options.
