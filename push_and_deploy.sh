git push origin --all;
git push gitee --all;
heroku maintenance:on;
git push heroku master;
heroku run flask deploy;
heroku maintenance:off;