curl -o ./output/post_deepcoadd_i13.fits -X POST \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $LSP_TOKEN" \
-d @../input/test_deepcoadd_i13.json \
-L https://$IS_EP/api/image/v1/DC_W13_Stripe82