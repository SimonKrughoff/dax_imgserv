curl -o ./output/post_deepcoadd_i14.fits -X POST \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $LSP_TOKEN" \
-d @../input/test_deepcoadd_i14.json \
http://$IS_EP/api/image/v1/DC_W14_Stripe82