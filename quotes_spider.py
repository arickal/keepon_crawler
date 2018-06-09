import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    
    start_urls = [ 'https://www.keepon.com.tw/forum-1-%d.html'%(i) 
        for i in range(1,2491) ]
        
    gpx_names = {}
    host = 'https://www.keepon.com.tw'

    def parse(self, response):
        for heading in response.css('h4.media-heading'):
            travelPage = self.host + heading.css('a::attr(href)').extract_first()
            yield scrapy.Request(travelPage, callback=self.parseGpxPage)

            
    def parseGpxPage(self, response):
        fnames = response.css('li.list-group-item a::attr(download)').extract()
        urls = response.css('li.list-group-item a::attr(href)').extract()
        for (file_name, url) in set(zip(fnames,urls)):
            if not file_name.endswith('.gpx'):
                continue
            self.gpx_names[ url.split('/')[-1]] = file_name
            gpx_url = self.host + url
            
            yield {
                'file_name' : file_name,
                'url' : response.url
            }
            
            yield scrapy.Request(gpx_url, callback=self.saveGpx)
            
            
    def saveGpx(self, response):
        path = response.url.split('/')[-1]
        file_name = self.gpx_names[path]
        with open( 'gpxfile/'+file_name, 'wb') as f:
            f.write(response.body)
