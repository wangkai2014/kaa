/*
 * Clutter.
 *
 * An OpenGL based 'interactive canvas' library.
 *
 * Authored By Matthew Allum  <mallum@openedhand.com>
 *
 * Copyright (C) 2006 OpenedHand
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 *
 * **************************************************************
 * Note: replace reflect_texture_render_to_gl_quad and 
 * clutter_reflect_texture_paint by functions from tidy!
 * Changed in r3347.
 * **************************************************************
 *
 */

#define CLUTTER_PARAM_READWRITE \
        G_PARAM_READABLE | G_PARAM_WRITABLE | G_PARAM_STATIC_NAME | G_PARAM_STATIC_NICK |G_PARAM_STATIC_BLURB


/**
 * SECTION:clutter-reflect-texture
 * @short_description: Actor for cloning existing textures in an 
 * efficient way.
 *
 * #ClutterReflectTexture allows the cloning of existing #ClutterTexture with 
 * a refelction like effect.
 */

#include <GL/gl.h>
#include <clutter/clutter.h>

#if CLUTTER_VERSION_HEX < 0x00070000
#   include <clutter/cogl.h>
#else
#   include <cogl/cogl.h>
#endif
#include "clutter-reflect-texture.h"

enum
{
  PROP_0,
  PROP_REFLECTION_HEIGHT
};

G_DEFINE_TYPE (ClutterReflectTexture,
	       clutter_reflect_texture,
	       CLUTTER_TYPE_CLONE_TEXTURE);

#define CLUTTER_REFLECT_TEXTURE_GET_PRIVATE(obj) \
(G_TYPE_INSTANCE_GET_PRIVATE ((obj), CLUTTER_TYPE_REFLECT_TEXTURE, ClutterReflectTexturePrivate))

struct _ClutterReflectTexturePrivate
{
  gint                 reflection_height;
};

static void
reflect_texture_render_to_gl_quad (ClutterReflectTexture *ctexture, 
				 ClutterTexture        *parent,
				 int             x1, 
				 int             y1, 
				 int             x2, 
				 int             y2)
{
  gint   qx1 = 0, qx2 = 0, qy1 = 0, qy2 = 0;
  gint   qwidth = 0, qheight = 0;
#if CLUTTER_VERSION_HEX < 0x00070000
  gint   x, y, i =0, lastx = 0, lasty = 0;
  gint   n_x_tiles, n_y_tiles; 
#endif

  gint   pwidth, pheight, rheight;
  float tx, ty, ty2 = 0.0;
  ClutterReflectTexturePrivate *priv = ctexture->priv;
  ClutterColor white = { 255, 255, 255, 255 };

  qwidth  = x2 - x1;
  qheight = y2 - y1;

  rheight = priv->reflection_height;
  if (rheight < 0)
    rheight = clutter_actor_get_height (CLUTTER_ACTOR (parent)) / 2;

  if (rheight > qheight)
    rheight = qheight;

  /* Only paint if parent is in a state to do so */
#if CLUTTER_VERSION_HEX < 0x00070000
  if (!clutter_texture_has_generated_tiles (parent))
    return;
#endif 
  clutter_texture_get_base_size (parent, &pwidth, &pheight); 

#if CLUTTER_VERSION_HEX < 0x00070000
  if (!clutter_texture_is_tiled (parent))
#else
  if (!cogl_texture_is_sliced(clutter_texture_get_cogl_texture(parent)))
#endif
    {
#if CLUTTER_VERSION_HEX < 0x00070000
      clutter_texture_bind_tile (parent, 0);
#endif

      /* NPOTS textures *always* used if extension available
       */
#if CLUTTER_VERSION_HEX < 0x00070000
      if (clutter_feature_available (CLUTTER_FEATURE_TEXTURE_RECTANGLE))
#else
      if (cogl_features_available(COGL_FEATURE_TEXTURE_RECTANGLE))
#endif
	{
	  tx = (float) pwidth;
	  ty = (float) pheight;
	  ty2 = (float)(clutter_actor_get_height (CLUTTER_ACTOR(ctexture)) * rheight) 
                                             / pheight;
	  ty2 = pheight - ty2;

	}
      else
	{
	  tx = (float) pwidth / clutter_util_next_p2 (pwidth);  
	  ty = (float) pheight / clutter_util_next_p2 (pheight);
	}

      qx1 = x1; qx2 = x2;
      qy1 = y1; qy2 = y1 + rheight;

#ifdef CLUTTER_COGL_HAS_GL
      glBegin (GL_QUADS);

      white.alpha = clutter_actor_get_opacity (CLUTTER_ACTOR (ctexture));
      cogl_color (&white);

      glTexCoord2f (0, ty);   
      glVertex2i   (qx1, qy1);

      glTexCoord2f (tx,  ty);   
      glVertex2i   (qx2, qy1);

      white.alpha = 0;
      cogl_color (&white);

      glTexCoord2f (tx,  ty2);    
      glVertex2i   (qx2, qy2);
      
      glTexCoord2f (0, ty2);    
      glVertex2i   (qx1, qy2);

      glEnd ();	
#else
#   warning "ClutterReflectTexture does not currently support GL ES"
#endif
      return;
    }

  /* FIXME: Below wont actually render the corrent graduated effect.
   * The code below is disabled for clutter 0.7+ as porting it is
   * non-trivial.
   */

  g_warning("ClutterReflectTexture doesn't support tiled textures."); 

#if defined(CLUTTER_COGL_HAS_GL) && CLUTTER_VERSION_HEX < 0x00070000

  clutter_texture_get_n_tiles (parent, &n_x_tiles, &n_y_tiles); 

  for (x = 0; x < n_x_tiles; x++)
    {
      lasty = 0;

      for (y = 0; y < n_y_tiles; y++)
	{
	  gint actual_w, actual_h;
	  gint xpos, ypos, xsize, ysize, ywaste, xwaste;
	  
	  clutter_texture_bind_tile (parent, i);
	 
	  clutter_texture_get_x_tile_detail (parent, x,
                                             &xpos, &xsize, &xwaste);
	  clutter_texture_get_y_tile_detail (parent, y,
                                             &ypos, &ysize, &ywaste);

	  actual_w = xsize - xwaste;
	  actual_h = ysize - ywaste;

	  tx = (float) actual_w / xsize;
	  ty = (float) actual_h / ysize;

	  qx1 = x1 + lastx;
	  qx2 = qx1 + ((qwidth * actual_w ) / pwidth );
	  
	  qy1 = y1 + lasty;
	  qy2 = qy1 + ((qheight * actual_h) / pheight );

	  glBegin (GL_QUADS);
	  glTexCoord2f (tx, ty);   glVertex2i   (qx2, qy2);
	  glTexCoord2f (0,  ty);   glVertex2i   (qx1, qy2);
	  glTexCoord2f (0,  0);    glVertex2i   (qx1, qy1);
	  glTexCoord2f (tx, 0);    glVertex2i   (qx2, qy1);
	  glEnd ();	

	  lasty += qy2 - qy1;	  

	  i++;
	}
      lastx += qx2 - qx1;
    }
#endif
}

static void
clutter_reflect_texture_paint (ClutterActor *self)
{
#ifdef CLUTTER_COGL_HAS_GL
  ClutterReflectTexture *texture;
  ClutterCloneTexture *clone;
  ClutterTexture *parent;
  ClutterActorBox box = { 0, };

  COGLenum target_type;
  ClutterColor white = { 255, 255, 255, 255 };

  texture = CLUTTER_REFLECT_TEXTURE (self);
  clone = CLUTTER_CLONE_TEXTURE (self);

  parent = clutter_clone_texture_get_parent_texture (clone);
  if (!parent)
    return;

  if (!CLUTTER_ACTOR_IS_REALIZED (parent))
    clutter_actor_realize (CLUTTER_ACTOR (parent));

#if CLUTTER_VERSION_HEX < 0x00070000
  if (clutter_feature_available (CLUTTER_FEATURE_TEXTURE_RECTANGLE) &&
      clutter_texture_is_tiled (parent) == FALSE)
#else
      if (cogl_features_available(COGL_FEATURE_TEXTURE_RECTANGLE) &&
          !cogl_texture_is_sliced(clutter_texture_get_cogl_texture(parent)))
#endif
    {
      target_type = CGL_TEXTURE_RECTANGLE_ARB;
#if CLUTTER_VERSION_HEX < 0x00070000
      cogl_enable (CGL_ENABLE_TEXTURE_RECT | CGL_ENABLE_BLEND);
#endif
    }
  else
    {
      target_type = CGL_TEXTURE_2D;
#if CLUTTER_VERSION_HEX < 0x00070000
      cogl_enable (CGL_ENABLE_TEXTURE_2D|CGL_ENABLE_BLEND);
#endif
    }
  
  cogl_push_matrix ();

  white.alpha = clutter_actor_get_opacity (self);
  cogl_color (&white);

#if CLUTTER_VERSION_HEX < 0x00070000
  clutter_actor_query_coords (self, &box);
#else
  clutter_actor_get_allocation_box (self, &box);
#endif

  reflect_texture_render_to_gl_quad (texture, parent,
                                     0, 0,
                                     CLUTTER_UNITS_TO_DEVICE (box.x2 - box.x1),
                                     CLUTTER_UNITS_TO_DEVICE (box.y2 - box.y1));

  cogl_pop_matrix ();
#endif
}



static void
clutter_reflect_texture_set_property (GObject      *object,
				    guint         prop_id,
				    const GValue *value,
				    GParamSpec   *pspec)
{
  ClutterReflectTexture         *ctexture = CLUTTER_REFLECT_TEXTURE (object);
  ClutterReflectTexturePrivate  *priv = ctexture->priv;  

  switch (prop_id)
    {
    case PROP_REFLECTION_HEIGHT:
      priv->reflection_height = g_value_get_int (value);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static void
clutter_reflect_texture_get_property (GObject    *object,
				    guint       prop_id,
				    GValue     *value,
				    GParamSpec *pspec)
{
  ClutterReflectTexture *ctexture = CLUTTER_REFLECT_TEXTURE (object);
  ClutterReflectTexturePrivate  *priv = ctexture->priv;  

  switch (prop_id)
    {
    case PROP_REFLECTION_HEIGHT:
      g_value_set_int (value, priv->reflection_height);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static void
clutter_reflect_texture_class_init (ClutterReflectTextureClass *klass)
{
  GObjectClass      *gobject_class = G_OBJECT_CLASS (klass);
  ClutterActorClass *actor_class = CLUTTER_ACTOR_CLASS (klass);

  actor_class->paint = clutter_reflect_texture_paint;

  gobject_class->set_property = clutter_reflect_texture_set_property;
  gobject_class->get_property = clutter_reflect_texture_get_property;

  g_object_class_install_property (gobject_class,
                                   PROP_REFLECTION_HEIGHT,
                                   g_param_spec_int ("reflection-height",
                                                     "Reflection Height",
                                                     "",
                                                     0, G_MAXINT,
                                                     0,
                                                     (G_PARAM_CONSTRUCT | CLUTTER_PARAM_READWRITE)));

  g_type_class_add_private (gobject_class, sizeof (ClutterReflectTexturePrivate));
}

static void
clutter_reflect_texture_init (ClutterReflectTexture *self)
{
  ClutterReflectTexturePrivate *priv;

  self->priv = priv = CLUTTER_REFLECT_TEXTURE_GET_PRIVATE (self);
  priv->reflection_height = 100; 
}

/**
 * clutter_reflect_texture_new:
 * @texture: a #ClutterTexture or %NULL
 *
 * Creates an efficient 'reflect' of a pre-existing texture if which it 
 * shares the underlying pixbuf data.
 *
 * You can use clutter_reflect_texture_set_parent_texture() to change the
 * parent texture to be reflectd.
 *
 * Return value: the newly created #ClutterReflectTexture
 */
ClutterActor *
clutter_reflect_texture_new (ClutterTexture *texture, gint reflection_height)
{
  g_return_val_if_fail (texture == NULL || CLUTTER_IS_TEXTURE (texture), NULL);

  return g_object_new (CLUTTER_TYPE_REFLECT_TEXTURE,
 		       "parent-texture", texture,
		       "reflection-height", reflection_height,
		       NULL);
}
