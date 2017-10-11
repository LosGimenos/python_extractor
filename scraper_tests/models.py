from django.db import models


class NoneCompatibleCharField(models.CharField):
    def get_prep_value(self, value):
        if value == 'None':
            return None
        return value

class Monitor(models.Model):
    monitorID = models.TextField(null=True, blank=True, db_index=True)
    keyword = models.TextField(null=True, blank=True)
    backfill_date = models.TextField(null=True, blank=True, db_index=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    def __str__(self):
        return "Monitor %s \n" % (self.monitorID.__str__())
    class Meta:
        ordering = ['id']

class Request(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "Create = %s" % (self.created.__str__())

class TwitterRequest(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "Create = %s" % (self.created.__str__())

class Brand(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True)
    brandName = models.TextField(null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Brand = %s" % (self.brandName.__str__())
    class Meta:
        ordering = ['id']

class Topic(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True)
    topicName = models.TextField(null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Topic = %s" % (self.topicName.__str__())
    class Meta:
        ordering = ['id']

class Post(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True)
    url = models.TextField(null=True, blank=True)
    statusID = models.TextField(null=True, blank=True)
    fbLocationUrl = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Post %s \n" % (self.url.__str__())
    class Meta:
        index_together = [('monitor', 'fbLocationUrl'),('monitor', 'statusID')]
    class Meta:
        ordering = ['id']

class Variable(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True)
    variableName = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Variable = %s" % (self.variableName.__str__())
    class Meta:
        ordering = ['id']

class PostData(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    value = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Participant %s \n" % (self.post.__str__())
    class Meta:
        index_together = ('monitor', 'post', 'variable')
    class Meta:
        ordering = ['id']

class Venue(models.Model):
    venueID = models.TextField(null=True, blank=True, db_index=True)
    twitterHandle = models.TextField(null=True, blank=True, db_index=True)
    instagramHandle = models.TextField(null=True, blank=True, db_index=True)
    latMin = models.FloatField()
    lonMin = models.FloatField()
    latMax = models.FloatField()
    lonMax = models.FloatField()
    def __str__(self):
        return "Venue = %s" % (self.venueID.__str__())
    class Meta:
        ordering = ['id']

class Bartender(models.Model):
    twitterHandle = models.TextField(null=True, blank=True, db_index=True)
    venueHandle = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Bartender = %s" % (self.twitterHandle.__str__())
    class Meta:
        ordering = ['id']

class InstagramGeolocation(models.Model):
    instagramUrl = models.TextField(null=True, blank=True, db_index=True)
    lat = models.FloatField()
    lon = models.FloatField()
    def __str__(self):
        return "Url = %s" % (self.instagramUrl.__str__())
    class Meta:
        ordering = ['id']

class Project(models.Model):
    project_id = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Project %s \n" % (self.project_id.__str__())
    class Meta:
        ordering = ['id']

class ProductPageUrl(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    source = models.TextField(null=True, blank=True, db_index=True)
    brand = models.TextField(null=True, blank=True, db_index=True)
    group = models.TextField(null=True, blank=True, db_index=True)
    product_line = models.TextField(null=True, blank=True, db_index=True)
    product = models.TextField(null=True, blank=True, db_index=True)
    url = models.TextField(null=True, blank=True, db_index=True)
    source_data_path = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Product Url = %s" % (self.url.__str__())
    class Meta:
        ordering = ['id']

class Product(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    source = models.TextField(null=True, blank=True, db_index=True)
    brand = models.TextField(null=True, blank=True, db_index=True)
    group = models.TextField(null=True, blank=True, db_index=True)
    product_line = models.TextField(null=True, blank=True, db_index=True)
    product = models.TextField(null=True, blank=True, db_index=True)
    average_rating = models.FloatField(null=True)
    total_number_reviews = models.IntegerField(null=True)
    num_reviews_one_star = models.IntegerField(null=True)
    num_reviews_two_stars = models.IntegerField(null=True)
    num_reviews_three_stars = models.IntegerField(null=True)
    num_reviews_four_stars = models.IntegerField(null=True)
    num_reviews_five_stars = models.IntegerField(null=True)
    def __str__(self):
        return "Product = %s" % (self.product_name.__str__())
    class Meta:
        ordering = ['id']

class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    review_id = models.TextField(null=True, blank=True, db_index=True)
    url = models.TextField(null=True, blank=True, db_index=True)
    date = models.DateTimeField(null=True)
    title = models.TextField(null=True, blank=True, db_index=True)
    username = models.TextField(null=True, blank=True, db_index=True)
    review_text = models.TextField(null=True, blank=True)
    rating = models.FloatField(null=True)
    total_who_voted = models.IntegerField(null=True)
    total_who_voted_helpful = models.IntegerField(null=True)
    num_comments = models.IntegerField(null=True)
    would_recommend = models.TextField(null=True, blank=True, db_index=True)
    is_from_brand_website = models.TextField(null=True, blank=True, db_index=True)
    skin_type = models.TextField(null=True, blank=True, db_index=True)
    gender = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Review = %s" % (self.review_id.__str__())
    class Meta:
        ordering = ['id']

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True)
    url = models.TextField(null=True, blank=True, db_index=True)
    date = models.DateTimeField(null=True)
    username = models.TextField(null=True, blank=True, db_index=True)
    comment_text = models.TextField(null=True, blank=True)
    total_who_voted = models.IntegerField(null=True)
    total_who_voted_helpful = models.IntegerField(null=True)
    is_brand_consumer_care = models.BooleanField(default=False)
    def __str__(self):
        return "Comment %s \n" % (self.username.__str__())
    class Meta:
        ordering = ['id']

class Dataset(models.Model):
    dataset_ID = models.TextField(null=True, blank=True, db_index=True)
    path = models.TextField(null=True, blank=True)
    dataset_name = models.TextField(null=True, blank=True, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    id_column = models.IntegerField(null=True)
    date_column = models.IntegerField(null=True)
    def __str__(self):
        return "Dataset %s \n" % (self.dataset_ID.__str__())
    class Meta:
        ordering = ['id']

class Column(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    column_name = models.TextField(null=True, blank=True, db_index=True)
    column_number = models.IntegerField(db_index=True, null=True)
    is_binary_variable = models.BooleanField(default=False)
    true_value = models.TextField(null=True, blank=True, db_index=True)
    false_value = models.TextField(null=True, blank=True, db_index=True)
    is_text_variable = models.BooleanField(default=False)
    is_number_variable = models.BooleanField(default=False)
    is_date_variable = models.BooleanField(default=False)
    def __str__(self):
        return "Column = %s" % (self.column_name.__str__())
    class Meta:
        ordering = ['id']

class Row(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    row_name = models.TextField(null=True, blank=True, db_index=True)
    row_number = models.IntegerField(db_index=True, null=True)
    matches_filters = models.BooleanField(default=True)
    matches_category = models.BooleanField(default=True)
    matches_split = models.BooleanField(default=True)
    def __str__(self):
        return "Row = %s" % (self.row_name.__str__())

class Data(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    row = models.ForeignKey(Row, on_delete=models.CASCADE, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True)
    number = models.FloatField(null=True)
    def __str__(self):
        return "Row %s \n" % (self.row.__str__())
    class Meta:
        index_together = ('dataset', 'row', 'column')

class Presentation(models.Model):
    presentation_name = models.TextField(null=True, blank=True, db_index=True)
    default_slide_layout_index = models.IntegerField(null=True, default=5)
    is_from_existing_presentation = models.BooleanField(default=False)
    existing_presentation_filename = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Presentation = %s" % (self.presentation_ID.__str__())
    class Meta:
        ordering = ['id']

class Slide(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, null=True)
    slide_layout_index = models.IntegerField(null=True)
    slide_name = models.TextField(null=True, blank=True, db_index=True)
    slide_type = models.TextField(null=True, blank=True, db_index=True)
    # Charts
    slide_number = models.IntegerField(null=True)
    number_grid_rows = models.IntegerField(null=True)
    number_grid_columns = models.IntegerField(null=True)
    width = models.FloatField(null=True)
    width_margin_left = models.FloatField(null=True)
    width_margin_right = models.FloatField(null=True)
    height = models.FloatField(null=True)
    height_margin_top = models.FloatField(null=True)
    height_margin_bottom = models.FloatField(null=True)
    def __str__(self):
        return "Slide = %s" % (self.slide_ID.__str__())
    class Meta:
        ordering = ['id']

class ChartStyle(models.Model):
    chart_style_name = models.TextField(null=True, blank=True, db_index=True)
    # title
    has_title = models.BooleanField(default=False)
    title_font_size = models.IntegerField(null=True)
    title_font_color_rgb_1 = models.IntegerField(null=True)
    title_font_color_rgb_2 = models.IntegerField(null=True)
    title_font_color_rgb_3 = models.IntegerField(null=True)
    title_is_bold = models.BooleanField(default=False)
    # legend
    has_legend = models.BooleanField(default=False)
    legend_position = models.TextField(null=True, blank=True, db_index=True)
    # Bottom, Corner, Left, Right, Top
    legend_font_size = models.IntegerField(null=True)
    legend_font_color_rgb_1 = models.IntegerField(null=True)
    legend_font_color_rgb_2 = models.IntegerField(null=True)
    legend_font_color_rgb_3 = models.IntegerField(null=True)
    # data labels
    has_data_labels = models.BooleanField(default=False)
    data_labels_number_format = models.TextField(null=True, blank=True, db_index=True)
    data_labels_font_size = models.IntegerField(null=True)
    data_labels_position = models.TextField(null=True, blank=True, db_index=True)
    # Above, Below, Center, Inside Base, Inside End, Left, Outside End, Right
    data_labels_font_color_rgb_1 = models.IntegerField(null=True)
    data_labels_font_color_rgb_2 = models.IntegerField(null=True)
    data_labels_font_color_rgb_3 = models.IntegerField(null=True)
    # category axis
    category_axis_has_major_gridlines = models.BooleanField(default=False)
    category_axis_has_minor_gridlines = models.BooleanField(default=False)
    category_axis_tick_labels_font_size = models.IntegerField(null=True)
    category_axis_tick_labels_font_color_rgb_1 = models.IntegerField(null=True)
    category_axis_tick_labels_font_color_rgb_2 = models.IntegerField(null=True)
    category_axis_tick_labels_font_color_rgb_3 = models.IntegerField(null=True)
    # value axis
    has_value_axis = models.BooleanField(default=False)
    has_data_labels = models.BooleanField(default=False)
    is_auto_min_max = models.BooleanField(default=True)
    value_axis_min_scale = models.FloatField(null=True)
    value_axis_max_scale = models.FloatField(null=True)
    value_axis_has_major_gridlines = models.BooleanField(default=False)
    value_axis_has_minor_gridlines = models.BooleanField(default=False)
    value_axis_tick_labels_number_format = models.TextField(null=True, blank=True, db_index=True)
    value_axis_tick_labels_are_bold = models.BooleanField(default=False)
    value_axis_tick_labels_font_size = models.IntegerField(null=True)
    value_axis_tick_labels_font_color_rgb_1 = models.IntegerField(null=True)
    value_axis_tick_labels_font_color_rgb_2 = models.IntegerField(null=True)
    value_axis_tick_labels_font_color_rgb_3 = models.IntegerField(null=True)
    def __str__(self):
        return "Chart Style = %s" % (self.id.__str__())
    class Meta:
        ordering = ['id']

class Chart(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    style = models.ForeignKey(ChartStyle, on_delete=models.SET_NULL, null=True)
    chart_name = models.TextField(null=True, blank=True, db_index=True)
    start_grid_row = models.IntegerField(null=True)
    start_grid_column = models.IntegerField(null=True)
    end_grid_row = models.IntegerField(null=True)
    end_grid_column = models.IntegerField(null=True)
    chart_type = models.TextField(null=True, blank=True, db_index=True)
    # Line, Line Markers, Pie, Cluster Column, Stacked Column, 100 Stacked Column,
    # Cluster Bar, Stacked Bar, 100 Stacked Bar, Area, Stacked Area, 100 Stacked Area,
    # Scatter, Bubble, Doughnut, Radar, Radar Markers
    filter_applied = models.BooleanField(default=False)
    is_sorted = models.BooleanField(default=False)
    sort_type = models.TextField(null=True, blank=True, db_index=True)
    # Category Alphabetical, Category Numerical, Series Numerical (Descending), Series Numerical (Ascending)
    has_category_max = models.BooleanField(default=False)
    number_max_categories = models.IntegerField(null=True)
    def __str__(self):
        return "Chart = %s" % (self.chart_ID.__str__())
    class Meta:
        ordering = ['id']

class Category(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, null=True)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, null=True)
    category_type = NoneCompatibleCharField(max_length=400, null=True, blank=True, db_index=True)
    # Value Based, Binary Variable Based
    is_all_binary_variables = models.BooleanField(default=False)
    category_variable = models.ForeignKey(Column, related_name='category_variable', on_delete=models.CASCADE, null=True)
    category_binary_variables = models.ManyToManyField(Column, related_name='category_binary_variables')
    def __str__(self):
        return "Category = %s" % (self.id.__str__())
    class Meta:
        ordering = ['id']

class Series(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, null=True)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, null=True)
    series_type = models.TextField(null=True, blank=True, db_index=True)
    # Count, Percentage Count, Sum, Percentage Sum, Average, Weighted Average
    denominator_type = models.TextField(null=True, blank=True, db_index=True)
    # All Rows, All Rows Minus Exclusions
    series_calculation_variable = models.ForeignKey(Column, related_name='series_calculation_variable', null=True)
    series_weighting_variable = models.ForeignKey(Column, related_name='series_weighting_variable', null=True)
    series_split_variable = models.ForeignKey(Column, related_name='series_split_variable', null=True)
    split_applied = models.BooleanField(default=False)
    def __str__(self):
        return "Category = %s" % (self.id.__str__())

class CategoryExclusion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Category Exclusion = %s" % (self.value.__str__())
    class Meta:
        ordering = ['id']

class SplitExclusion(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Split Exclusion = %s" % (self.value.__str__())
    class Meta:
        ordering = ['id']

class Filter(models.Model):
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, null=True)
    value = models.TextField(null=True, blank=True, db_index=True)
    def __str__(self):
        return "Filter = %s" % (self.value.__str__())
    class Meta:
        ordering = ['id']

class PowerpointBuild(models.Model):
    path = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    class Meta:
        ordering = ['id']
