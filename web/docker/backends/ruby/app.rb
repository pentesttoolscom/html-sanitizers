require 'sinatra'
require 'nokogiri'
require 'rails-html-sanitizer'
require 'sanitize'

set :port, 80
set :bind, '0.0.0.0' # Bind to all interfaces

class Sanitize
  module Config
    HTTP_PROTOCOLS = %w(
      http
      https
    ).freeze

    LINK_PROTOCOLS = %w(
      http
      https
      dat
      dweb
      ipfs
      ipns
      ssb
      gopher
      xmpp
      magnet
      gemini
    ).freeze

    CLASS_WHITELIST_TRANSFORMER = lambda do |env|
      node = env[:node]
      class_list = node['class']&.split(/[\t\n\f\r ]/)

      return unless class_list

      class_list.keep_if do |e|
        next true if /^(h|p|u|dt|e)-/.match?(e) # microformats classes
        next true if /^(mention|hashtag)$/.match?(e) # semantic classes
        next true if /^(ellipsis|invisible)$/.match?(e) # link formatting classes
      end

      node['class'] = class_list.join(' ')
    end

    TRANSLATE_TRANSFORMER = lambda do |env|
      node = env[:node]
      node.remove_attribute('translate') unless node['translate'] == 'no'
    end

    UNSUPPORTED_HREF_TRANSFORMER = lambda do |env|
      return unless env[:node_name] == 'a'

      current_node = env[:node]

      scheme = if current_node['href'] =~ Sanitize::REGEX_PROTOCOL
                 Regexp.last_match(1).downcase
               else
                 :relative
               end

      current_node.replace(Nokogiri::XML::Text.new(current_node.text, current_node.document)) unless LINK_PROTOCOLS.include?(scheme)
    end

    UNSUPPORTED_ELEMENTS_TRANSFORMER = lambda do |env|
      return unless %w(h1 h2 h3 h4 h5 h6).include?(env[:node_name])

      current_node = env[:node]

      current_node.name = 'strong'
      current_node.wrap('<p></p>')
    end

    MASTODON_STRICT = freeze_config(
      elements: %w(p br span a del pre blockquote code b strong u i em ul ol li),

      attributes: {
        'a' => %w(href rel class translate),
        'span' => %w(class translate),
        'ol' => %w(start reversed),
        'li' => %w(value),
      },

      add_attributes: {
        'a' => {
          'rel' => 'nofollow noopener noreferrer',
          'target' => '_blank',
        },
      },

      protocols: {},

      transformers: [
        CLASS_WHITELIST_TRANSFORMER,
        TRANSLATE_TRANSFORMER,
        UNSUPPORTED_ELEMENTS_TRANSFORMER,
        UNSUPPORTED_HREF_TRANSFORMER,
      ]
    )

    MASTODON_OEMBED = freeze_config(
      elements: %w(audio embed iframe source video),

      attributes: {
        'audio' => %w(controls),
        'embed' => %w(height src type width),
        'iframe' => %w(allowfullscreen frameborder height scrolling src width),
        'source' => %w(src type),
        'video' => %w(controls height loop width),
      },

      protocols: {
        'embed' => { 'src' => HTTP_PROTOCOLS },
        'iframe' => { 'src' => HTTP_PROTOCOLS },
        'source' => { 'src' => HTTP_PROTOCOLS },
      },

      add_attributes: {
        'iframe' => { 'sandbox' => 'allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-forms' },
      }
    )
  end
end

get '/' do
  send_file File.join(settings.public_folder, 'index.html')
end

get '/rails-html-sanitizer' do
  html_input = params['text'] || ''
  begin
    Rails::Html::WhiteListSanitizer.allowed_tags << 'a'
    Rails::Html::WhiteListSanitizer.allowed_attributes.merge(['href', 'target', 'rel'])
    sanitizer = Rails::Html::SafeListSanitizer.new
    sanitized_html = sanitizer.sanitize(html_input)
    return sanitized_html
  rescue Exception => e
    status 500
    return e.message
  end
end

get '/rgrove-sanitize' do
  html_input = params['text'] || ''
  begin
    oembed_html = Sanitize.fragment(html_input, Sanitize::Config::MASTODON_OEMBED)
    strict_html = Sanitize.fragment(html_input, Sanitize::Config::MASTODON_STRICT)
    return "Strict: #{strict_html}\nOembed: #{oembed_html}"
  rescue Exception => e
    status 500
    return e.message
  end
end
