#coding=utf-8
import scrapy
from ..items import VideoItem
import re

#Code: Tom Tang
class WeChatSpider(scrapy.Spider):
    name = "jingcaishipin-gechangjia-tencent"
    all_class = {
        'https://v.qq.com/x/search/?ses=qid%3DYoHhQ7lIVaqps0qjtjer-Cp8BsNWRM-cq0wB13FuPIxfzXT1nd-0gw':'蒋大为',
        'https://v.qq.com/x/search/?ses=qid%3DYCFdUynbyziwpkODn9VAwVAgKZmkKQnq9d0E6cQIrA4rImIS6cbh7g':'李谷一',
        'https://v.qq.com/x/search/?ses=qid%3De9RH9-GSQCGjbO9L77uosL4Ymco0EmDBE62pzOL-uea-Ig4rIazjAw':'阎维文',
        'https://v.qq.com/x/search/?ses=qid%3D5j9odb74GrG_9PQnmCHtE_ukRvQZMVsiJozcK2FFjU_gbuf5DWl29A':'刘和刚',
        'https://v.qq.com/x/search/?ses=qid%3Dj-mhahWBLAOeqJEJssXJBTnM3q_sijxSdSPIIdaa82Ahc01QCc_e4g':'关牧村',
        'https://v.qq.com/x/search/?ses=qid%3D5Z0xK7HUT1DPI2uDydFd_bNJe-Pz5Kw5EdbyLq4BOQ2lIMATtxd_Qg':'胡松华',
        'https://v.qq.com/x/search/?ses=qid%3D6uRY-sj3vck2QNVS5tAikKJ5Aka08PFh1VLXIMsQs44EjaR3w-x5rA':'于淑珍',
        'https://v.qq.com/x/search/?ses=qid%3DgsX8aXVQkmlHAg0dJIoYNKScrPLVQeibHIOVLLuv5b0MInx0uTyMSg':'马玉涛',
        'https://v.qq.com/x/search/?ses=qid%3D4BFfXFOv7heaudnCoEF69zQtual007iqVtdXb8pC0hx-gwQGOfZJLA':'刘秉义',
        'https://v.qq.com/x/search/?ses=qid%3D40bkmEIPyPBnYxOQMsFr3jpNouZvKSd24Im_E78N2HkcCw3TlcT__A':'德德玛',
        'https://v.qq.com/x/search/?ses=qid%3DCfKnLyGuCaAWKJ4MutUOMkaKa61Ban2GW-MYeAegy5IPJiurCSOcXQ':'邓玉华',
        'https://v.qq.com/x/search/?ses=qid%3De43lrIUQ_6IAJ5bEwBwLMQg2SD2r4ydDaAN9ZHNyw_8IQG7dHk5tGQ':'张也经',
        'https://v.qq.com/x/search/?ses=qid%3D2feJFiR72zWcVnCvaCdv52mFQds4sMKquvjS5RMdHOTyzGQPazdTwQ':'耿莲凤',
        'https://v.qq.com/x/search/?ses=qid%3DD0NBBh7Fmm4ij5zC-MfIl-m9W5F1SuC1r4izvC2AydcSpC3UE2d_Lw':'李丹阳',
        'https://v.qq.com/x/search/?ses=qid%3D9D3JuXr6G4B_2Fbt5waPLowLXmxylGtr8xl3WuqJp__lu5Z8OphmyA':'祖海',
        'https://v.qq.com/x/search/?ses=qid%3D0PxZKkxZwt3BmoZEwvIZLOt6kYKSuK7CEb9xsfQFvuBl_YvK6eMalw':'郑绪岚',
        'https://v.qq.com/x/search/?ses=qid%3DH2DvZL2c856vGdAatFPYUHToW1yM6LXnR6dDNA3smlQ95VWPp53_jw':'李双江',
        'https://v.qq.com/x/search/?ses=qid%3DsotagwIOYsgam7JKCoju6DVQIgwS3YfkEVXcz3BtelBB_z9zWaRplg':'才旦卓玛',
        'https://v.qq.com/x/search/?ses=qid%3DEIKnBxjG54q9kDjZT9Pk7CpI0mwFsGOoLr1oIZgRb5Cz2CGjHttbKA':'叶佩英',
        'https://v.qq.com/x/search/?ses=qid%3Dp9DEEZdnX7ghys0bDV27Q5oxoANLrQFIyTGq1akQX8ofuL5-j9rlEQ':'吴雁泽',
        'https://v.qq.com/x/search/?ses=qid%3DRSDp_QUkgbCrwbePD4EoxGhOvdZK8i9N8_tyfYKytknXrytTreDHGw':'胡松华'
    }

    start_urls = ['https://v.qq.com/x/search/?ses=qid%3DYoHhQ7lIVaqps0qjtjer-Cp8BsNWRM-cq0wB13FuPIxfzXT1nd-0gw%26last_query%3D%E8%92%8B%E5%A4%A7%E4%B8%BA%E7%BB%8F%E5%85%B8%E6%AD%8C%E6%9B%B2%26tabid_list%3D0%7C5%7C3%7C7%7C12%7C20%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E5%A8%B1%E4%B9%90%7C%E6%AF%8D%E5%A9%B4&q=%E8%92%8B%E5%A4%A7%E4%B8%BA%E7%BB%8F%E5%85%B8%E6%AD%8C%E6%9B%B2&stag=3&cur=1&cxt=tabid%3D0%26sort%3D2%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DYCFdUynbyziwpkODn9VAwVAgKZmkKQnq9d0E6cQIrA4rImIS6cbh7g%26last_query%3D%E6%9D%8E%E8%B0%B7%E4%B8%80%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C3%7C12%7C7%7C1%7C11%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E5%A8%B1%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E6%95%99%E8%82%B2&q=%E6%9D%8E%E8%B0%B7%E4%B8%80%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3De9RH9-GSQCGjbO9L77uosL4Ymco0EmDBE62pzOL-uea-Ig4rIazjAw%26last_query%3D%E9%98%8E%E7%BB%B4%E6%96%87%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C1%7C11%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90&q=%E9%98%8E%E7%BB%B4%E6%96%87%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D5j9odb74GrG_9PQnmCHtE_ukRvQZMVsiJozcK2FFjU_gbuf5DWl29A%26last_query%3D%E5%88%98%E5%92%8C%E5%88%9A%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C7%7C3%7C5%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E9%9F%B3%E4%B9%90%7C%E5%A8%B1%E4%B9%90&q=%E5%88%98%E5%92%8C%E5%88%9A%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D1%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3Dj-mhahWBLAOeqJEJssXJBTnM3q_sijxSdSPIIdaa82Ahc01QCc_e4g%26last_query%3D%E5%85%B3%E7%89%A7%E6%9D%91%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C2%7C1%7C11%7C12%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90%7C%E6%95%99%E8%82%B2&q=%E5%85%B3%E7%89%A7%E6%9D%91%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D2%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D5Z0xK7HUT1DPI2uDydFd_bNJe-Pz5Kw5EdbyLq4BOQ2lIMATtxd_Qg%26last_query%3D%E8%83%A1%E6%9D%BE%E5%8D%8E%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C7%7C3%7C5%7C1%7C6%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E9%9F%B3%E4%B9%90%7C%E7%94%B5%E5%BD%B1%7C%E7%BA%AA%E5%BD%95%E7%89%87%7C%E5%A8%B1%E4%B9%90&q=%E8%83%A1%E6%9D%BE%E5%8D%8E%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D2%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D6uRY-sj3vck2QNVS5tAikKJ5Aka08PFh1VLXIMsQs44EjaR3w-x5rA%26last_query%3D%E4%BA%8E%E6%B7%91%E7%8F%8D%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C3%7C7%7C5%7C1%7C6%7C12%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E7%94%B5%E5%BD%B1%7C%E7%BA%AA%E5%BD%95%E7%89%87%7C%E5%A8%B1%E4%B9%90%7C%E6%95%99%E8%82%B2&q=%E4%BA%8E%E6%B7%91%E7%8F%8D%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DgsX8aXVQkmlHAg0dJIoYNKScrPLVQeibHIOVLLuv5b0MInx0uTyMSg%26last_query%3D%E9%A9%AC%E7%8E%89%E6%B6%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C1%7C3%7C12%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E5%BD%B1%7C%E7%BB%BC%E8%89%BA%7C%E5%A8%B1%E4%B9%90%7C%E6%95%99%E8%82%B2&q=%E9%A9%AC%E7%8E%89%E6%B6%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D2%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D4BFfXFOv7heaudnCoEF69zQtual007iqVtdXb8pC0hx-gwQGOfZJLA%26last_query%3D%E5%88%98%E7%A7%89%E4%B9%89%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C11%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90&q=%E5%88%98%E7%A7%89%E4%B9%89%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D40bkmEIPyPBnYxOQMsFr3jpNouZvKSd24Im_E78N2HkcCw3TlcT__A%26last_query%3D%E5%BE%B7%E5%BE%B7%E7%8E%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C2%7C11%7C12%7C17%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90%7C%E6%B8%B8%E6%88%8F&q=%E5%BE%B7%E5%BE%B7%E7%8E%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DCfKnLyGuCaAWKJ4MutUOMkaKa61Ban2GW-MYeAegy5IPJiurCSOcXQ%26last_query%3D%E9%82%93%E7%8E%89%E5%8D%8E%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C7%7C5%7C3%7C1%7C11%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90&q=%E9%82%93%E7%8E%89%E5%8D%8E%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3De43lrIUQ_6IAJ5bEwBwLMQg2SD2r4ydDaAN9ZHNyw_8IQG7dHk5tGQ%26last_query%3D%E5%BC%A0%E4%B9%9F%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C1%7C11%7C12%7C17%7C13%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90%7C%E6%B8%B8%E6%88%8F%7C%E8%B4%A2%E7%BB%8F&q=%E5%BC%A0%E4%B9%9F%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D2feJFiR72zWcVnCvaCdv52mFQds4sMKquvjS5RMdHOTyzGQPazdTwQ%26last_query%3D%E8%80%BF%E8%8E%B2%E5%87%A4%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C3%7C1%7C11%7C7%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%85%B6%E4%BB%96&q=%E8%80%BF%E8%8E%B2%E5%87%A4%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DD0NBBh7Fmm4ij5zC-MfIl-m9W5F1SuC1r4izvC2AydcSpC3UE2d_Lw%26last_query%3D%E6%9D%8E%E4%B8%B9%E9%98%B3%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C2%7C1%7C3%7C11%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%94%B5%E5%BD%B1%7C%E7%BB%BC%E8%89%BA%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90&q=%E6%9D%8E%E4%B8%B9%E9%98%B3%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D9D3JuXr6G4B_2Fbt5waPLowLXmxylGtr8xl3WuqJp__lu5Z8OphmyA%26last_query%3D%E7%A5%96%E6%B5%B7%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C7%7C3%7C1%7C12%7C8%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%BB%BC%E8%89%BA%7C%E7%94%B5%E5%BD%B1%7C%E5%A8%B1%E4%B9%90%7C%E5%8E%9F%E5%88%9B&q=%E7%A5%96%E6%B5%B7%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3D0PxZKkxZwt3BmoZEwvIZLOt6kYKSuK7CEb9xsfQFvuBl_YvK6eMalw%26last_query%3D%E9%83%91%E7%BB%AA%E5%B2%9A%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C3%7C7%7C2%7C1%7C11%7C12%7C8%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90%7C%E5%8E%9F%E5%88%9B&q=%E9%83%91%E7%BB%AA%E5%B2%9A%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DH2DvZL2c856vGdAatFPYUHToW1yM6LXnR6dDNA3smlQ95VWPp53_jw%26last_query%3D%E6%9D%8E%E5%8F%8C%E6%B1%9F%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C5%7C3%7C7%7C2%7C1%7C11%7C12%7C15%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%94%B5%E5%BD%B1%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90%7C%E6%95%99%E8%82%B2&q=%E6%9D%8E%E5%8F%8C%E6%B1%9F%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DsotagwIOYsgam7JKCoju6DVQIgwS3YfkEVXcz3BtelBB_z9zWaRplg%26last_query%3D%E6%89%8D%E6%97%A6%E5%8D%93%E7%8E%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C3%7C7%7C5%7C11%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E6%96%B0%E9%97%BB%7C%E5%A8%B1%E4%B9%90&q=%E6%89%8D%E6%97%A6%E5%8D%93%E7%8E%9B%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DEIKnBxjG54q9kDjZT9Pk7CpI0mwFsGOoLr1oIZgRb5Cz2CGjHttbKA%26last_query%3D%E5%8F%B6%E4%BD%A9%E8%8B%B1%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C3%7C7%7C5%7C6%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E7%BB%BC%E8%89%BA%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E7%BA%AA%E5%BD%95%E7%89%87&q=%E5%8F%B6%E4%BD%A9%E8%8B%B1%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D1%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3Dp9DEEZdnX7ghys0bDV27Q5oxoANLrQFIyTGq1akQX8ofuL5-j9rlEQ%26last_query%3D%E5%90%B4%E9%9B%81%E6%B3%BD%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8%26tabid_list%3D0%7C7%7C5%7C15%7C1%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E5%85%B6%E4%BB%96%7C%E9%9F%B3%E4%B9%90%7C%E6%95%99%E8%82%B2%7C%E7%94%B5%E5%BD%B1%7C%E5%A8%B1%E4%B9%90&q=%E5%90%B4%E9%9B%81%E6%B3%BD%E6%AD%8C%E6%9B%B2%E5%A4%A7%E5%85%A8&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0',
'https://v.qq.com/x/search/?ses=qid%3DRSDp_QUkgbCrwbePD4EoxGhOvdZK8i9N8_tyfYKytknXrytTreDHGw%26last_query%3D%E8%83%A1%E6%9D%BE%E5%8D%8E%E7%BB%8F%E5%85%B8%E6%AD%8C%E6%9B%B2%26tabid_list%3D0%7C5%7C7%7C1%7C3%7C6%7C12%26tabname_list%3D%E5%85%A8%E9%83%A8%7C%E9%9F%B3%E4%B9%90%7C%E5%85%B6%E4%BB%96%7C%E7%94%B5%E5%BD%B1%7C%E7%BB%BC%E8%89%BA%7C%E7%BA%AA%E5%BD%95%E7%89%87%7C%E5%A8%B1%E4%B9%90&q=%E8%83%A1%E6%9D%BE%E5%8D%8E%E7%BB%8F%E5%85%B8%E6%AD%8C%E6%9B%B2&stag=3&cur=1&cxt=tabid%3D0%26sort%3D0%26pubfilter%3D0%26duration%3D0'
]

    def parse(self, response):
        url_ori = response.xpath('/html/body/div[2]/div[2]/div[1]//a/@href').extract()
        url_lists = list(set(url_ori))

        for url_next in url_lists:
            if '/x/page' in url_next:
                req = scrapy.Request(url=url_next, callback=self.tencent_parseinfo)
                item = VideoItem()
                item["sourceUrl"] = url_next
                item['className'] = self.all_class[response.url[:91]]
                req.meta["m_item"] = item
                yield req

        nextPage_ori = response.url.split('&')
        nextPage = ''
        for each in nextPage_ori:
            if each[:-1] == 'cur=':
                currentPage = int(each.split('=')[-1])
                nextPageNum = currentPage + 1
                if nextPageNum > 20:
                    return
                else:
                    nextPage = nextPage + 'cur=' + str(nextPageNum) + '&'
            else:
                nextPage = nextPage + each + '&'
        req_next = scrapy.Request(url=nextPage[:-1], callback=self.parse)
        yield req_next

    def tencent_parseinfo(self, response):
        page_url = response.url
        vid = page_url.split('/')[-1].split('.')[0]
        url = "https://v.qq.com/iframe/player.html?vid=" + vid + "&tiny=0&auto=0"
        title_ori = response.xpath('//div[@class="mod_intro"]/div/h1/text()').extract()[0]
        title = ""
        for i in range(len(title_ori)):
            if title_ori[i] != '\n':
                if title_ori[i] != ' ':
                    if title_ori[i] != '\t':
                        title = title +title_ori[i]

        item1 = response.meta["m_item"]
        if len(title) == 0:
            return

        item1["module"] = "歌唱家"
        item1["title"] = title
        item1["source"] = "腾讯视频"
        item1["url"] = url
        item1["poster"] = None
        item1["edition"] = None

        yield item1
