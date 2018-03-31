$(function() {

	//产品列表分类切换
	var oGl = 0;
	$(".GLindex").eq(oGl).addClass("GLindexClick")
	$(".goodsList").eq(oGl).show()
	$(".GLindex").click(function() {
		oGl = $(".GLindex").index(this)
		$(".GLindex").removeClass("GLindexClick").eq(oGl).addClass("GLindexClick")
		$(".goodsList").hide().eq(oGl).show()
	})

	//产品列表购物车
	$(".goShoppingcartBtn").click(function() {
		$(".GWC").toggle();
		//$(".GWC").show();
		$(".mack").show();
		$(".Control_bar").css({
			"position": "fixed"
		});
	})
	$(".mackbg").click(function() {
			$(".layerBox").hide();
			$(".mack").hide();
			$(".Control_bar").css({
				"position": ""
			});
		})
	
		//购物车 end
		//在线预约
	$(function() {
		$(".online_tab li").eq(0).addClass("tabon");
		$(".online_tab li").click(function() {
			$(".online_tab li").removeClass("tabon");
			$(this).addClass("tabon");
		})
	})

	$(function() {
			$(".yyjs").hide();
			$(".yyjs").eq(0).show();
			$(".online_tab li").click(function() {
				x = $(".online_tab li").index(this);
				$(".yyjs").hide();
				$(".yyjs").eq(x).show();
			});
		})
		//在线预约 end

	/*我的预约*/
	$(".goodsdetail-btn").click(function() {
			var con = $(this).parent().next(".goodsdetail-con");
			if(con.is(":visible") == false) {

				$(this).children("img").attr("src", "images/detailmoreup.png");
				con.slideDown(333);

			} else {

				$(this).children("img").attr("src", "images/detailmorer.png");
				con.slideUp(333)
			}
		})
		/*我的预约end*/
})