<pre>
     ___       ___                    ___
    /\  \     /\  \                  /\__\
   /::\  \   /::\  \                /:/ _/_
  /:/\:\__\ /:/\:\__\              /:/ /\  \
 /:/ /:/  //:/ /:/  /___     ___  /:/ /::\  \
/:/_/:/  //:/_/:/  //\  \   /\__\/:/_/:/\:\__\
\:\/:/  / \:\/:/  / \:\  \ /:/  /\:\/:/ /:/  /
 \::/__/   \::/__/   \:\  /:/  /  \::/ /:/  /
  \:\  \    \:\  \    \:\/:/  /    \/_/:/  /
   \:\__\    \:\__\    \::/  /       /:/  /
    \/__/     \/__/     \/__/        \/__/

</pre>

## Probabilistic Production Log Summarizer

This program simplifies your production logs using a combination of probabilistic and exact near(est)-neighbor clustering techniques. The goal is to **automagically** produce a very good representative subset of your log even with important volume of data.

## Usage example:
> python main.py --fuzzy_fields log_message,100 --exact_fields severity --similarity_threshold 0.89 --logfile log_samples/error_log  --log_format errorlog_apache

## Supported log formats:
With a bit of plugin coding, it is posible to analyse virtually any kind of textual logs (see exemple at the end of this page). But out of the box, we support:

- Webserver access logs : apache/nginx
- Application server : weblogic
- syslog

## Dependencies:
The following libraries are required to run PPLS
* python-Levenshtein
* redis (optional)
* IPython \[notebook\] (optional)

## References
The algorithms used in this project are mainly inspired from chapter 3 of the excellent book: [Mining of Massive Datasets] (http://infolab.stanford.edu/~ullman/mmds.html)
